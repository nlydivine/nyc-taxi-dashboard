import os
import sys
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import get_connection

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

def get_db():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"message": "API is running"})

@app.route("/trips", methods=["GET"])
def get_trips():
    limit = request.args.get("limit", default=5000, type=int)
    skip = request.args.get("skip", default=0, type=int)
    borough = request.args.get("borough")
    min_distance = request.args.get("minDistance", type=float)
    max_distance = request.args.get("maxDistance", type=float)

    query = """
        SELECT
            t.trip_id AS id,
            REPLACE(t.tpep_pickup_datetime, ' ', 'T') AS pickup_datetime,
            puz.Borough AS pickup_borough,
            doz.Borough AS dropoff_borough,
            puz.Zone AS pickup_zone,
            doz.Zone AS dropoff_zone,
            t.trip_distance AS trip_distance,
            t.trip_duration_minutes AS trip_duration_min,
            t.fare_amount AS fare_amount,
            t.tip_amount AS tip_amount,
            t.total_amount AS total_amount,
            ROUND(t.total_amount / NULLIF(t.trip_distance, 0), 2) AS cost_per_mile,
            t.avg_speed_mph AS avg_speed_mph
        FROM trips t
        JOIN zones puz ON t.PULocationID = puz.LocationID
        JOIN zones doz ON t.DOLocationID = doz.LocationID
        WHERE 1=1
    """
    params = []
    if borough and borough != "all":
        query += " AND puz.Borough = ?"
        params.append(borough)
    if min_distance is not None:
        query += " AND t.trip_distance >= ?"
        params.append(min_distance)
    if max_distance is not None:
        query += " AND t.trip_distance <= ?"
        params.append(max_distance)

    query += " ORDER BY t.trip_id LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trips WHERE trip_id = ?", [trip_id])
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Trip not found"}), 404
    return jsonify(dict(row))

@app.route("/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) AS total_trips,
            ROUND(AVG(fare_amount), 2) AS avg_fare,
            ROUND(AVG(trip_distance), 2) AS avg_distance,
            ROUND(AVG(trip_duration_minutes), 2) AS avg_duration_minutes,
            ROUND(AVG(avg_speed_mph), 2) AS avg_speed_mph,
            ROUND(AVG(tip_percentage), 2) AS avg_tip_percentage
        FROM trips
    """)
    row = cursor.fetchone()
    conn.close()
    return jsonify(dict(row))

@app.route("/columns", methods=["GET"])
def get_columns():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(trips)")
    rows = cursor.fetchall()
    conn.close()
    columns = [row["name"] for row in rows]
    return jsonify({"columns": columns})

time_index = []

def build_index():
    global time_index
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tpep_pickup_datetime, trip_id FROM trips ORDER BY tpep_pickup_datetime ASC")
    time_index = [(row["tpep_pickup_datetime"], row["trip_id"]) for row in cursor.fetchall()]
    conn.close()

def window_start(target):
    lo = 0
    hi = len(time_index)
    while lo < hi:
        mid = (lo + hi) // 2
        if time_index[mid][0] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def window_end(target):
    lo = 0
    hi = len(time_index)
    while lo < hi:
        mid = (lo + hi) // 2
        if time_index[mid][0] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

@app.route("/search", methods=["GET"])
def search_trips():
    time_from = request.args.get("from")
    time_to = request.args.get("to")
    if not time_from or not time_to:
        return jsonify({"error": "from and to datetime required"}), 400
    if not time_index:
        build_index()
    start = window_start(time_from)
    end = window_end(time_to)
    ids = [trip_id for (pickup_time, trip_id) in time_index[start:end]]
    if not ids:
        return jsonify([])
    conn = get_db()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in ids)
    cursor.execute(f"SELECT * FROM trips WHERE trip_id IN ({placeholders}) ORDER BY tpep_pickup_datetime ASC", ids)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

