from flask import Flask, request, jsonify, render_template
import json
import time
import os

app = Flask(__name__)

# 数据存储路径
DATA_FILE = "sensor_data.json"

# 确保数据文件存在
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump([], file)

# 获取存储的数据
def get_stored_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

# 保存数据到文件
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
        
        # 验证数据格式
        if "temperature" in data and "humidity" in data and "time" in data:
            # 获取现有数据
            stored_data = get_stored_data()
            
            # 添加新数据
            stored_data.append(data)
            
            # 仅保留最近的1000条记录
            if len(stored_data) > 1000:
                stored_data = stored_data[-1000:]
            
            # 保存数据
            save_data(stored_data)
            
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "数据格式不正确"}), 400
    else:
        return jsonify({"status": "error", "message": "请求不是JSON格式"}), 400

@app.route("/data", methods=["GET"])
def get_data():
    # 获取数据并返回
    data = get_stored_data()
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 