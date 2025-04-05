import time
import board
import adafruit_dht

# 初始化DHT11传感器（假设连接到GPIO4）
dht_device = adafruit_dht.DHT11(board.D4)

def read_sensor():
    try:
        # 读取温湿度
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        return humidity, temperature
    except RuntimeError as e:
        # 传感器通信错误处理（常见于时序问题）
        print(f"读取失败: {e}")
        return None, None
    except Exception as e:
        # 其他异常处理
        print(f"未知错误: {e}")
        return None, None

if __name__ == "__main__":
    try:
        while True:
            humidity, temperature = read_sensor()
            if humidity is not None and temperature is not None:
                print(f"湿度: {humidity}%, 温度: {temperature}℃")
            else:
                print("数据无效，等待重试...")
            time.sleep(2)  # 每2秒读取一次（DHT11最大采样率1Hz）[[1]][[9]]
    except KeyboardInterrupt:
        print("程序终止")
    finally:
        dht_device.exit()  # 释放资源