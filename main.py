import time
import json
import os
import threading
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import dht11
from flask import Flask, request, jsonify, render_template
import snowboydecoder
import sys
import signal

# 数据存储路径
DATA_FILE = "sensor_data.json"

# 关键词检测模型路径
MODEL_PATH = "pi.pmdl"  # 请确保替换为你的模型文件

# 全局变量，用于存储最新的传感器数据
current_temperature = 0
current_humidity = 0
data_lock = threading.Lock()
sensor_data = []

# 关键词检测中断标志
interrupted = False

# 关键词触发冷却时间（秒）
COOLDOWN_TIME = 60  # 1分钟冷却时间
last_trigger_time = 0  # 上次触发时间
cooldown_lock = threading.Lock()  # 用于保护last_trigger_time的锁

# 在主线程中设置信号处理器
def setup_signal_handlers():
    signal.signal(signal.SIGINT, signal_handler)
    print("信号处理器已设置")

# 信号处理函数
def signal_handler(signal_number, frame):
    global interrupted
    print(f"收到信号 {signal_number}")
    interrupted = True

# 中断检查回调函数
def interrupt_callback():
    global interrupted
    return interrupted

# 确保数据文件存在
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as file:
        json.dump([], file)

# 加载已有数据
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

# 初始化Flask应用
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data", methods=["GET"])
def get_data():
    # 获取数据并返回
    with data_lock:
        return jsonify(sensor_data), 200

# 初始化OLED
def init_oled():
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
    
    # 创建空白图像
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    
    # 加载支持中文的字体
    try:
        # 检查simhei.ttf是否存在于当前目录
        if os.path.exists('simhei.ttf'):
            font = ImageFont.truetype('simhei.ttf', 12)
        # 如果不在当前目录，可能在系统字体目录
        elif os.path.exists('/usr/share/fonts/truetype/simhei.ttf'):
            font = ImageFont.truetype('/usr/share/fonts/truetype/simhei.ttf', 12)
        elif os.path.exists('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'):
            font = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 12)
        else:
            # 如果找不到指定字体，使用默认英文字体
            font = ImageFont.load_default()
            print("警告: 未找到中文字体，将使用默认字体，中文可能无法正确显示")
    except Exception as e:
        font = ImageFont.load_default()
        print(f"加载字体出错: {e}，将使用默认字体")
    
    return oled, image, draw, font

# 更新OLED显示
def update_display(oled, image, draw, font, humidity, temperature):
    # 清空显示
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    
    # 显示文字
    draw.text((0, 0), f"Temperature: {temperature}C", font=font, fill=255)
    draw.text((0, 20), f"Humidity: {humidity}%", font=font, fill=255)
    
    # 刷新显示
    oled.image(image)
    oled.show()

# 语音播报当前温湿度
def speak_temperature_humidity():
    global current_temperature, current_humidity, last_trigger_time
    
    # 检查是否在冷却时间内
    with cooldown_lock:
        current_time = time.time()
        time_since_last_trigger = current_time - last_trigger_time
        
        if time_since_last_trigger < COOLDOWN_TIME:
            remaining_time = int(COOLDOWN_TIME - time_since_last_trigger)
            print(f"冷却时间内，还需等待 {remaining_time} 秒才能再次播报")
            return False  # 在冷却时间内，不播报
        
        # 更新上次触发时间
        last_trigger_time = current_time
    
    with data_lock:
        temp = current_temperature
        humidity = current_humidity
    
    # 格式化播报内容
    temp_str = f"当前温度 {temp:.1f} 摄氏度"
    humi_str = f"湿度 {humidity:.1f} 百分比"
    
    print("检测到关键词，正在播报温湿度...")
    print(temp_str)
    print(humi_str)
    
    # 使用espeak播报温湿度（英文）
    os.system(f'espeak "Current temperature is {temp:.1f} degrees Celsius"')
    os.system(f'espeak "Humidity is {humidity:.1f} percent"')
    
    return True  # 播报成功

# 关键词检测回调函数
def detected_callback():
    # 检查是否在冷却时间内
    with cooldown_lock:
        current_time = time.time()
        time_since_last_trigger = current_time - last_trigger_time
        
        if time_since_last_trigger < COOLDOWN_TIME:
            remaining_time = int(COOLDOWN_TIME - time_since_last_trigger)
            print(f"检测到关键词，但在冷却时间内，还需等待 {remaining_time} 秒")
            return  # 在冷却时间内，不响应
    
    # 播放一个音频文件提示检测到了关键词
    snowboydecoder.play_audio_file()
    # 语音播报当前温湿度
    speak_temperature_humidity()

# 传感器数据收集线程
def sensor_thread():
    global current_temperature, current_humidity, sensor_data
    
    # 初始化OLED
    oled, image, draw, font = init_oled()
    
    # 加载已存储的数据
    with data_lock:
        sensor_data = get_stored_data()
    
    print("传感器线程已启动")
    
    try:
        print("正在初始化I2C...")
        i2c = busio.I2C(board.SCL, board.SDA)
        print("I2C初始化成功")
        # 其他初始化步骤...
        
        while True:
            # 读取传感器数据
            humidity, temperature = dht11.read_sensor()
            
            if humidity is not None and temperature is not None:
                print(f"温度: {temperature}°C, 湿度: {humidity}%")
                
                # 更新OLED显示
                update_display(oled, image, draw, font, humidity, temperature)
                
                # 更新全局变量
                with data_lock:
                    current_temperature = temperature
                    current_humidity = humidity
                    
                    # 添加新数据
                    new_data = {
                        "time": time.time(),
                        "temperature": temperature,
                        "humidity": humidity
                    }
                    sensor_data.append(new_data)
                    
                    # 仅保留最近的1000条记录
                    if len(sensor_data) > 1000:
                        sensor_data = sensor_data[-1000:]
                    
                    # 每10次读取保存一次数据到文件
                    if len(sensor_data) % 10 == 0:
                        save_data(sensor_data)
            else:
                print("传感器读取失败")
            
            # 等待一段时间再读取
            time.sleep(3)  # 每3秒读取一次
    except KeyboardInterrupt:
        print("传感器线程已终止")
        # 清空显示
        oled.fill(0)
        oled.show()
    except Exception as e:
        print(f"传感器线程错误: {e}")
    finally:
        # 保存数据
        with data_lock:
            save_data(sensor_data)

# Flask服务器线程
def flask_thread():
    print("Web服务器已启动，访问 http://[你的树莓派IP]:5000 查看网页")
    # 以调试模式关闭、线程模式开启的方式运行Flask
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

# 关键词检测线程
def hotword_thread():
    global interrupted
    
    # 检查模型文件是否存在
    if not os.path.exists(MODEL_PATH):
        print(f"错误: 找不到关键词检测模型 {MODEL_PATH}")
        print("提示: 请确保下载了关键词检测模型并放在正确的位置")
        return
    
    # 不再在线程中设置信号处理器
    # signal.signal(signal.SIGINT, signal_handler) # 移除这行
    
    # 初始化检测器
    detector = snowboydecoder.HotwordDetector(MODEL_PATH, sensitivity=0.5)
    print('关键词检测已启动...说出关键词来获取当前温湿度')
    
    try:
        # 主循环
        detector.start(detected_callback=detected_callback,
                      interrupt_check=interrupt_callback,
                      sleep_time=0.03)
    except Exception as e:
        print(f"关键词检测错误: {e}")
    finally:
        # 终止检测器
        detector.terminate()
        print("关键词检测线程已终止")

# 主函数
def main():
    print("温湿度监测系统启动中...")
    
    # 在主线程中设置信号处理器
    setup_signal_handlers()
    
    # 创建传感器线程
    sensor = threading.Thread(target=sensor_thread)
    sensor.daemon = True  # 设为守护线程，主线程结束时自动结束
    
    # 创建Web服务器线程
    server = threading.Thread(target=flask_thread)
    server.daemon = True  # 设为守护线程，主线程结束时自动结束
    
    # 创建关键词检测线程
    hotword = threading.Thread(target=hotword_thread)
    hotword.daemon = True  # 设为守护线程，主线程结束时自动结束
    
    # 启动线程
    sensor.start()
    server.start()
    hotword.start()
    
    try:
        # 主线程保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("程序正在终止...")
        # 设置中断标志
        global interrupted
        interrupted = True
        # 保存数据
        with data_lock:
            save_data(sensor_data)
        print("数据已保存，程序已终止")

if __name__ == "__main__":
    main() 