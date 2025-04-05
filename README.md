# 温湿度监测系统

这是一个基于Raspberry Pi的温湿度监测系统，使用DHT11传感器采集温湿度数据，通过OLED屏幕显示，并将数据上传到Web服务器展示温湿度折线图。

## 功能特点

- 使用DHT11传感器采集温湿度数据
- 在OLED屏幕上实时显示温度和湿度
- 将采集的数据上传到Web服务器
- Web页面展示温湿度实时折线图
- 数据定时自动刷新

## 硬件需求

- Raspberry Pi (任何型号都可以)
- DHT11温湿度传感器
- SSD1306 OLED显示屏 (128x64像素)
- 连接线

## 接线说明

DHT11接线:
- VCC -> 3.3V
- GND -> GND
- DATA -> GPIO4 (可在dht11.py中修改)

OLED接线:
- VCC -> 3.3V
- GND -> GND
- SCL -> GPIO SCL
- SDA -> GPIO SDA

## 软件依赖

```bash
pip install adafruit-circuitpython-dht
pip install adafruit-circuitpython-ssd1306
pip install pillow
pip install flask
pip install requests
```

## 使用方法

1. 按照接线说明连接DHT11传感器和OLED显示屏
2. 安装所需的软件依赖
3. 启动Web服务器

```bash
python server.py
```

4. 在另一个终端启动主程序

```bash
python main.py
```

5. 打开浏览器访问 `http://localhost:5000` 查看温湿度折线图

## 文件说明

- `dht11.py`: DHT11传感器驱动程序
- `oled.py`: OLED显示屏驱动程序
- `main.py`: 主程序，整合传感器读取和显示功能
- `server.py`: Web服务器，接收和存储数据
- `templates/index.html`: Web页面模板，显示温湿度折线图
- `sensor_data.json`: 数据存储文件

## 注意事项

- DHT11传感器的最大采样率为1Hz，建议读取间隔不小于2秒
- 如需外网访问，请在启动服务器时设置合适的主机和端口，并配置相应的网络安全设置
- 数据存储默认最多保留1000条记录，可在server.py中修改 