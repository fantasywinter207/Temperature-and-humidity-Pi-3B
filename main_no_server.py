import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import dht11
import os

# 初始化OLED
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

def main():
    try:
        print("温湿度监测已启动，按Ctrl+C停止...")
        
        while True:
            # 读取传感器数据
            humidity, temperature = dht11.read_sensor()
            
            if humidity is not None and temperature is not None:
                print(f"温度: {temperature}°C, 湿度: {humidity}%")
                
                # 更新OLED显示
                update_display(humidity, temperature)
            else:
                print("传感器读取失败")
            
            # 等待一段时间再读取
            time.sleep(2)  # 每2秒读取一次
    except KeyboardInterrupt:
        print("程序已终止")
        # 清空显示
        oled.fill(0)
        oled.show()

if __name__ == "__main__":
    main() 