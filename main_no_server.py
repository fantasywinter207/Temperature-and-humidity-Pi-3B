import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import dht11
import os

# ��ʼ��OLED
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# �����հ�ͼ��
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# ����֧�����ĵ�����
try:
    # ���simhei.ttf�Ƿ�����ڵ�ǰĿ¼
    if os.path.exists('simhei.ttf'):
        font = ImageFont.truetype('simhei.ttf', 12)
    # ������ڵ�ǰĿ¼��������ϵͳ����Ŀ¼
    elif os.path.exists('/usr/share/fonts/truetype/simhei.ttf'):
        font = ImageFont.truetype('/usr/share/fonts/truetype/simhei.ttf', 12)
    else:
        # ����Ҳ���ָ�����壬ʹ��Ĭ��Ӣ������
        font = ImageFont.load_default()
        print("����: δ�ҵ��������壬��ʹ��Ĭ�����壬���Ŀ����޷���ȷ��ʾ")
except Exception as e:
    font = ImageFont.load_default()
    print(f"�����������: {e}����ʹ��Ĭ������")

def update_display(humidity, temperature):
    # �����ʾ
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    
    # ��ʾ����
    draw.text((0, 0), f"Temperature: {temperature}C", font=font, fill=255)
    draw.text((0, 20), f"Humidity: {humidity}%", font=font, fill=255)
    
    # ˢ����ʾ
    oled.image(image)
    oled.show()

def main():
    try:
        print("��ʪ�ȼ������������Ctrl+Cֹͣ...")
        
        while True:
            # ��ȡ����������
            humidity, temperature = dht11.read_sensor()
            
            if humidity is not None and temperature is not None:
                print(f"�¶�: {temperature}��C, ʪ��: {humidity}%")
                
                # ����OLED��ʾ
                update_display(humidity, temperature)
            else:
                print("��������ȡʧ��")
            
            # �ȴ�һ��ʱ���ٶ�ȡ
            time.sleep(2)  # ÿ2���ȡһ��
    except KeyboardInterrupt:
        print("��������ֹ")
        # �����ʾ
        oled.fill(0)
        oled.show()

if __name__ == "__main__":
    main() 