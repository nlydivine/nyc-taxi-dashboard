from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = "../nyc_taxi.db"

# -------------------------
# DB CONNECTION
# -------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
# HEALTH CHECK
# -------------------------
@app.route("/")
def home():
    return jsonify({"status": "NYC Taxi API running"})

# -------------------------
# GET ALL TRIPS
# -------------------------
@app.route("/trips")
def get_trips():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trips LIMIT 100")
    rows = cursor.fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])

# -------------------------
# GET TRIP COUNT
# -------------------------
@app.route("/trips/count")
def trip_count():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM trips")
    result = cursor.fetchone()

    conn.close()
    return jsonify(dict(result))

# -------------------------
# GET ZONES
# -------------------------
@app.route("/zones")
def get_zones():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM zones")
    rows = cursor.fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])

# -------------------------
# AVG FARE (INSIGHT QUERY)
# -------------------------
@app.route("/stats/avg_fare")
def avg_fare():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT AVG(fare_amount) as avg_fare FROM trips")
    result = cursor.fetchone()

    conn.close()
    return jsonify(dict(result))

# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
