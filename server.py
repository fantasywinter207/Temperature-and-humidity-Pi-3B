from flask import Flask, request, jsonify, render_template
import json
import time
import os

app = Flask(__name__)

# Data storage path
DATA_FILE = "sensor_data.json"

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump([], file)

# Get stored data
def get_stored_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

# Save data to file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data", methods=["POST"])
def receive_data():
    if request.is_json:
        data = request.get_json()
        
        # Validate data format
        if "temperature" in data and "humidity" in data and "time" in data:
            # Get existing data
            stored_data = get_stored_data()
            
            # Add new data
            stored_data.append(data)
            
            # Keep only the most recent 1000 records
            if len(stored_data) > 1000:
                stored_data = stored_data[-1000:]
            
            # Save data
            save_data(stored_data)
            
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400
    else:
        return jsonify({"status": "error", "message": "Request is not in JSON format"}), 400

@app.route("/data", methods=["GET"])
def get_data():
    # Get and return data
    data = get_stored_data()
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)