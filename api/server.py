import os
import sys
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

#find the db when run from anywhere
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import get_connection

app = Flask(__name__)
CORS(app)

def get_db():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "API is running"})

@app.route("/trips", methods=["GET"])
def get_trips():
    limit = request.args.get("limit", default=100, type=int)
    skip = request.args.get("skip", default=0, type=int)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trips LIMIT ? OFFSET ?", [limit, skip])
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

#DSA
time_index = []

def build_index():
    global time_index
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT tpep_pickup_datetime, trip_id FROM trips ORDER BY tpep_pickup_datetime ASC")
    time_index = [(row["tpep_pickup_datetime"], row["trip_id"]) for row in cursor.fetchall()]
    conn.close()

def window_start(target):  #left pointer
    lo = 0
    hi = len(time_index)
    while lo < hi:
        mid = (lo + hi) // 2
        if time_index[mid][0] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def window_end(target):  #right pointer
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