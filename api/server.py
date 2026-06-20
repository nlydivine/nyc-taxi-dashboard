from flask import Flask
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def get_db():
    conn = sqlite3.connect("nyc_taxi.db")
    return conn

@app.route("/")
def home():
    return {"status": "API working"}

@app.route("/trips")
def trips():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM trips")
    count = cursor.fetchone()[0]
    conn.close()
    return {"trip_count": count}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
