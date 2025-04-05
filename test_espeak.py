import os

# 模拟温湿度数据
humidity = 50.0
temperature = 25.0

# 格式化播报内容
temp_str = f"Temperature is {temperature:.1f} degrees Celsius."
humi_str = f"Humidity is {humidity:.1f} percent."

# 打印到终端（可选）
print(temp_str)
print(humi_str)

# 使用 espeak 播报温湿度
os.system(f'espeak "{temp_str}"')
os.system(f'espeak "{humi_str}"')