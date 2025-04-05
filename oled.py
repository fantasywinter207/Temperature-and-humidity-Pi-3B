import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# 初始化 I2C 接口
i2c = busio.I2C(board.SCL, board.SDA)

# 创建 SSD1306 对象（根据实际屏幕分辨率调整）
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# 清屏
oled.fill(0)
oled.show()

# 创建一个空白图像（模式为 1 表示单色）
image = Image.new("1", (oled.width, oled.height))

# 获取绘图对象
draw = ImageDraw.Draw(image)

# 加载默认字体
font = ImageFont.load_default()

# 显示文字
text = "Hello, Raspberry Pi!"
draw.text((0, 0), text, font=font, fill=255)

# 将图像显示到 OLED 屏幕
oled.image(image)
oled.show()