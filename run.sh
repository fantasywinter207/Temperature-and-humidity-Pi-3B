#!/bin/bash

# 编译代码
g++ main.cpp oled.cpp dht11.cpp -o program -lgpiod

# 检查编译是否成功
if [ $? -eq 0 ]; then
    # 赋予可执行权限
    chmod +x program
    # 运行程序
    sudo ./program
else
    echo "编译失败，请检查错误信息。"
fi