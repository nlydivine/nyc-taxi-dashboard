from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "API is running"})


@app.route("/trips", methods=["GET"])
def get_trips():
    pass


@app.route("/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    pass


@app.route("/stats", methods=["GET"])
def get_stats():
    pass


@app.route("/columns", methods=["GET"])
def get_columns():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)