# 家庭天气监测系统

这是一个基于树莓派的家庭天气监测系统，能够实时监测室内温度和湿度，并提供Web界面进行数据可视化。系统还支持语音关键词检测，通过语音指令获取当前温湿度信息。

## 功能特点

- 实时监测室内温度和湿度
- OLED屏幕显示当前环境数据
- Web服务器提供数据可视化界面
- 数据自动保存，支持历史数据查看
- 支持中文显示（需安装中文字体）
- 语音关键词检测，说出唤醒词可获取当前温湿度信息
- 多线程设计，传感器监测、Web服务器和语音检测同时工作

## 硬件要求

- 树莓派（Raspberry Pi）
- DHT11温湿度传感器
- SSD1306 OLED显示屏（I2C接口）
- 麦克风（用于语音检测）
- 扬声器（用于语音播报）
- 连接线和面包板

## 接线方式

- DHT11数据引脚连接到GPIO4
- OLED显示屏通过I2C接口连接（SDA和SCL引脚）
- 麦克风和扬声器根据具体型号连接

## 安装步骤

1. 安装必要的系统依赖：

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-smbus i2c-tools espeak
```

2. 启用I2C接口：

```bash
sudo raspi-config
# 选择 "Interface Options" -> "I2C" -> "Yes"
```

3. 安装Python依赖：

```bash
pip3 install flask adafruit-circuitpython-ssd1306 adafruit-circuitpython-dht requests
```

4. 下载并安装Snowboy语音检测工具：

```bash
# 按照Snowboy官方文档安装必要依赖
# 获取Snowboy项目文件并安装
```

5. 下载本项目代码：

```bash
git clone <项目仓库地址>
cd home_weather
```

6. （可选）安装中文字体以支持OLED中文显示：

```bash
sudo apt-get install -y fonts-wqy-zenhei
# 或复制simhei.ttf到项目目录
```

7. 准备语音关键词模型：

```bash
# 确保pi.pmdl文件存在于项目根目录
# 或使用Snowboy工具训练自己的关键词模型
```

## 使用方法

1. 启动主程序（集成了所有功能）：

```bash
python3 main.py
```

2. 打开网页浏览器，访问：

```
http://<树莓派IP地址>:5000
```

3. 对着麦克风说出你设置的关键词（默认为"Pi"），系统将语音播报当前温湿度

## 主要文件说明

- `main.py`: 集成的主程序，包含传感器监测、Web服务器和语音检测功能
- `dht11.py`: DHT11温湿度传感器接口
- `oled.py`: OLED显示屏控制
- `snowboydecoder.py`: Snowboy语音检测解码器
- `snowboydetect.py`: Snowboy语音检测引擎
- `pi.pmdl`: 语音关键词模型文件
- `templates/index.html`: Web界面

## 系统工作原理

本系统基于多线程设计，主要包含三个线程：
1. 传感器线程：每3秒读取一次温湿度数据，更新OLED显示，并保存数据
2. Web服务器线程：提供Web界面，显示实时和历史温湿度数据
3. 语音检测线程：持续监听关键词，触发后播报当前温湿度

系统采用线程锁机制保证数据一致性，并设置了语音触发的冷却时间（默认60秒），避免频繁触发。

## 注意事项

- 确保DHT11和OLED屏幕正确连接到树莓派
- 如需在OLED上显示中文，请安装相应字体
- 传感器可能会出现偶尔读取失败的情况，这是正常现象
- 数据存储在`sensor_data.json`文件中，默认保留最近1000条记录
- 语音关键词需要在安静环境中使用，避免环境噪音干扰
- 语音触发有60秒的冷却时间，避免频繁触发

## 问题排查

- 如果OLED无法显示，检查I2C连接和地址设置
- 如果传感器数据持续无法读取，检查DHT11连接和电源
- 如果Web界面无法访问，确保服务器正在运行且端口未被占用
- 如果语音关键词检测不工作，检查麦克风连接和模型文件路径
- 如果语音播报无声音，检查扬声器连接和espeak安装

## 贡献与反馈

=======
# 家庭天气监测系统

这是一个基于树莓派的家庭天气监测系统，能够实时监测室内温度和湿度，并提供Web界面进行数据可视化。系统还支持语音关键词检测，通过语音指令获取当前温湿度信息。

## 功能特点

- 实时监测室内温度和湿度
- OLED屏幕显示当前环境数据
- Web服务器提供数据可视化界面
- 数据自动保存，支持历史数据查看
- 支持中文显示（需安装中文字体）
- 语音关键词检测，说出唤醒词可获取当前温湿度信息
- 多线程设计，传感器监测、Web服务器和语音检测同时工作

## 硬件要求

- 树莓派（Raspberry Pi）
- DHT11温湿度传感器
- SSD1306 OLED显示屏（I2C接口）
- 麦克风（用于语音检测）
- 扬声器（用于语音播报）
- 连接线和面包板

## 接线方式

- DHT11数据引脚连接到GPIO4
- OLED显示屏通过I2C接口连接（SDA和SCL引脚）
- 麦克风和扬声器根据具体型号连接

## 安装步骤

1. 安装必要的系统依赖：

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-smbus i2c-tools espeak
```

2. 启用I2C接口：

```bash
sudo raspi-config
# 选择 "Interface Options" -> "I2C" -> "Yes"
```

3. 安装Python依赖：

```bash
pip3 install flask adafruit-circuitpython-ssd1306 adafruit-circuitpython-dht requests
```

4. 下载并安装Snowboy语音检测工具：

```bash
# 按照Snowboy官方文档安装必要依赖
# 获取Snowboy项目文件并安装
```

5. 下载本项目代码：

```bash
git clone <项目仓库地址>
cd home_weather
```

6. （可选）安装中文字体以支持OLED中文显示：

```bash
sudo apt-get install -y fonts-wqy-zenhei
# 或复制simhei.ttf到项目目录
```

7. 准备语音关键词模型：

```bash
# 确保pi.pmdl文件存在于项目根目录
# 或使用Snowboy工具训练自己的关键词模型
```

## 使用方法

1. 启动主程序（集成了所有功能）：

```bash
python3 main.py
```

2. 打开网页浏览器，访问：

```
http://<树莓派IP地址>:5000
```

3. 对着麦克风说出你设置的关键词（默认为"Pi"），系统将语音播报当前温湿度

## 主要文件说明

- `main.py`: 集成的主程序，包含传感器监测、Web服务器和语音检测功能
- `dht11.py`: DHT11温湿度传感器接口
- `oled.py`: OLED显示屏控制
- `snowboydecoder.py`: Snowboy语音检测解码器
- `snowboydetect.py`: Snowboy语音检测引擎
- `pi.pmdl`: 语音关键词模型文件
- `templates/index.html`: Web界面

## 系统工作原理

本系统基于多线程设计，主要包含三个线程：
1. 传感器线程：每3秒读取一次温湿度数据，更新OLED显示，并保存数据
2. Web服务器线程：提供Web界面，显示实时和历史温湿度数据
3. 语音检测线程：持续监听关键词，触发后播报当前温湿度

系统采用线程锁机制保证数据一致性，并设置了语音触发的冷却时间（默认60秒），避免频繁触发。

## 注意事项

- 确保DHT11和OLED屏幕正确连接到树莓派
- 如需在OLED上显示中文，请安装相应字体
- 传感器可能会出现偶尔读取失败的情况，这是正常现象
- 数据存储在`sensor_data.json`文件中，默认保留最近1000条记录
- 语音关键词需要在安静环境中使用，避免环境噪音干扰
- 语音触发有60秒的冷却时间，避免频繁触发

## 问题排查

- 如果OLED无法显示，检查I2C连接和地址设置
- 如果传感器数据持续无法读取，检查DHT11连接和电源
- 如果Web界面无法访问，确保服务器正在运行且端口未被占用
- 如果语音关键词检测不工作，检查麦克风连接和模型文件路径
- 如果语音播报无声音，检查扬声器连接和espeak安装

## 贡献与反馈

>>>>>>> origin/master
欢迎提交问题报告和改进建议！ 
