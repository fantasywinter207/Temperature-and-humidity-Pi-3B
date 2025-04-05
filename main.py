import time
import json
import requests
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import dht11
import os

# 服务器地址设置
SERVER_URL = "http://localhost:5000/data"

# 初始化OLED
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# 创建空白图像
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# 加载支持中文的字体
# 尝试加载simhei.ttf，如果不存在则使用默认字体
try:
    # 检查simhei.ttf是否存在于当前目录
    if os.path.exists('simhei.ttf'):
        font = ImageFont.truetype('simhei.ttf', 12)
    # 如果不在当前目录，可能在系统字体目录
    elif os.path.exists('/usr/share/fonts/truetype/simhei.ttf'):
        font = ImageFont.truetype('/usr/share/fonts/truetype/simhei.ttf', 12)
    else:
        # 如果找不到指定字体，使用默认英文字体
        font = ImageFont.load_default()
        print("警告: 未找到中文字体，将使用默认字体，中文可能无法正确显示")
except Exception as e:
    font = ImageFont.load_default()
    print(f"加载字体出错: {e}，将使用默认字体")

def update_display(humidity, temperature):
    # 清空显示
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    
    # 显示文字
    draw.text((0, 0), f"Temperature: {temperature}C", font=font, fill=255)
    draw.text((0, 20), f"Humidity: {humidity}%", font=font, fill=255)
    
    # 刷新显示
    oled.image(image)
    oled.show()

def upload_data(humidity, temperature):
    try:
        data = {
            "time": time.time(),
            "temperature": temperature,
            "humidity": humidity
        }
        # 设置较短的超时时间，避免长时间等待
        response = requests.post(SERVER_URL, json=data, timeout=2)
        if response.status_code == 200:
            print("数据上传成功")
            return True
        else:
            print(f"上传失败: HTTP状态码 {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("警告: 无法连接到服务器，只在OLED上显示数据")
        return False
    except requests.exceptions.Timeout:
        print("警告: 服务器连接超时，只在OLED上显示数据")
        return False
    except Exception as e:
        print(f"上传错误: {e}")
        return False

def main():
    try:
        print("温湿度监测已启动，按Ctrl+C停止...")
        print("提示: 如需使用Web功能，请确保在另一个终端中运行了server.py")
        
        while True:
            # 读取传感器数据
            humidity, temperature = dht11.read_sensor()
            
            if humidity is not None and temperature is not None:
                print(f"温度: {temperature}°C, 湿度: {humidity}%")
                
                # 更新OLED显示
                update_display(humidity, temperature)
                
                # 上传数据到服务器
                upload_data(humidity, temperature)
            else:
                print("传感器读取失败")
            
            # 等待一段时间再读取
            time.sleep(10)  # 每10秒读取并上传一次
    except KeyboardInterrupt:
        print("程序已终止")
        # 清空显示
        oled.fill(0)
        oled.show()

if __name__ == "__main__":
    main() 