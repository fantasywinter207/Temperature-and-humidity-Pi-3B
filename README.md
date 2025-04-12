
# Real-Time Environmental Monitoring System for Raspberry Pi  


## 1. Project Overview  
### Project Name  
Real-Time Environmental Monitoring System for Raspberry Pi  

### Project Description  
An embedded system developed for Raspberry Pi, integrating temperature/humidity monitoring, OLED data display, data storage, and voice interaction. Suitable for smart homes, greenhouses, and small-scale industrial monitoring. Uses C++ for hardware drivers and Python for web services and voice functions, balancing performance and development efficiency.  

### Core Advantages  
- **Realtime Performance**: Thread prioritization and multi-threading ensure non-blocking sensor data collection and interface refresh.  
- **Modular Design**: Separation of hardware drivers (DHT11, OLED) and software services (Web, Voice) for easy expansion and maintenance.  
- **User Interaction**: Supports voice queries and anomaly alerts, reducing operational complexity.  


## 2. Key Functional Features  

### 1. Real-Time Temperature/Humidity Monitoring  
- **Hardware Support**: DHT11 sensor (connected to GPIO4), with data validation and outlier filtering.  
- **Data Collection**:  
  - Real-time sampling at 1-second intervals, implemented via `readData()` in `dht11.cpp` for sensor communication and checksum verification.  
  - Returns `std::nullopt` on validation failure to avoid invalid data entry.  
- **Threshold Alerts**:  
  - Temperature: 10°C ~ 40°C, Humidity: 20% ~ 95%.  
  - Voice warnings ("Current temperature is too high, please ventilate!") and OLED flashing for out-of-range values.  

### 2. OLED Visualization  
- **Hardware Connection**: 128x32 I2C OLED display (GPIO2/SDA, GPIO3/SCL).  
- **Display Content**:  
  - **Time**: Real-time date (YYYY-MM-DD) on page 0.  
  - **Temperature**: 0.1°C precision, format: "TEMPERATURE: X.X°C" (page 2).  
  - **Humidity**: 0.1% precision, format: "HUMIDITY: X.X%" (page 4).  
- **Refresh Mechanism**: Auto-clears and redraws data every 60 seconds for clarity.  

### 3. Data Storage & Web API  
- **Local Storage**:  
  - Data stored in `sensor_data.json` (JSON format), retaining up to 1000 historical records.  
  - Includes timestamp, temperature, and humidity fields, supporting resume on breakpoint and file recovery.  
- **Web Services**:  
  - Flask-based RESTful API:  
    - **POST /data**: Upload real-time data (Content-Type: application/json).  
    - **GET /data**: Retrieve historical data for frontend display or analysis.  

### 4. Voice Interaction System  
- **Speech Recognition**:  
  - Wake word "computer" activates the Vosk model, supporting English/Chinese commands (language packs required).  
  - Recognizes queries like "What's the humidity?" or "Exit system", with <1.5s response time (tested on Raspberry Pi 4B).  
- **Speech Synthesis**:  
  - pyttsx3 engine for voice feedback, adjustable speech rate (150 words/minute) and volume.  
  - Auto-broadcasts anomalies (e.g., "Warning: Humidity below 20%, please increase humidity!").  


## 3. Technical Architecture & Implementation  

### 1. Hardware Architecture  
| Component       | Model/Specification | Function               | Connection       |  
|-----------------|---------------------|------------------------|------------------|  
| Main Board      | Raspberry Pi 4B (4GB)| System control         | N/A              |  
| Sensor          | DHT11               | Temp/humidity collection| GPIO4 (BCM)      |  
| Display         | 128x32 OLED         | Data visualization     | I2C (GPIO2/SDA, GPIO3/SCL) |  

### 2. Software Architecture  
```  
Raspberry Pi OS (Raspbian)  
├─ C++ Hardware Driver Layer  
│  ├─ DHT11 Class (dht11.h/cpp): Sensor communication and data validation  
│  └─ OLED Class (oled.h/cpp): I2C protocol and text rendering  
├─ Python Service Layer  
│  ├─ Flask Web Server (server.py): Data storage and API  
│  └─ Voice Assistant (speak.py): Speech recognition, synthesis, and alerts  
└─ Main Program (main.cpp): Multi-thread integration of drivers and services  
```  

### 3. Key Technical Points  
- **Multi-Threading**:  
  - `std::async` in `main.cpp` starts Web server and voice assistant in the background, avoiding blocking the sensor collection loop.  
  - Highest thread priority for sensor reading (`set_max_priority`) to ensure realtime response.  
- **Memory-Mapped GPIO**:  
  - Direct GPIO register access via `mmap` in `dht11.cpp` for high-speed communication (requires root privileges).  
- **Cross-Language Collaboration**:  
  - C++ for high-performance hardware drivers, Python for I/O-bound tasks (network requests, speech synthesis), balancing efficiency and development speed.  


## 4. Quick Start & Usage Guide  

### 1. Hardware Wiring  
| DHT11 Pin | Raspberry Pi Physical Pin | BCM GPIO Number |  
|-----------|---------------------------|-----------------|  
| VCC       | 2/4 (5V)                  | -               |  
| DATA      | 7                         | GPIO4           |  
| GND       | 6                         | -               |  

The OLED display connects via I2C; enable I2C in `raspi-config` before use.  

### 2. Software Installation  
#### Step 1: Clone Repository  
```bash  
git clone https://github.com/your-username/raspberrypi-env-monitor.git  
cd raspberrypi-env-monitor  
```  

#### Step 2: Set Up Python Environment  
```bash  
# Create virtual environment  
python3 -m venv dht11_env  
# Activate (Linux/macOS)  
source dht11_env/bin/activate  
# Install dependencies  
pip install flask vosk pyttsx3 requests  
```  

#### Step 3: Compile C++ Drivers  
```bash  
g++ -o main main.cpp dht11.cpp oled.cpp -lgpiod -std=c++11  
```  

### 3. System Startup Commands  
```bash  
# 1. Start web server (background)  
python3 server.py &  
# 2. Launch voice assistant (background)  
python3 speak.py &  
# 3. Run main program (foreground, Ctrl+C to stop)  
./main  
```  

### 4. Voice Command List  
| Command Type   | Example Command         | System Response                     |  
|----------------|-------------------------|-------------------------------------|  
| Wake Command   | "computer"              | "How can I help you?"               |  
| Temp/Humid Query| "what's the temperature"| "Current temperature is 25.5°C"     |  
| Time Query     | "what's the time"       | "The current time is 14:30"         |  
| Exit Command   | "exit"                  | "Goodbye!" (stops all services)     |  


## 5. Code Structure & Module Description  

### 1. Directory Structure  
```  
Project Root  
├── src/                # C++ Source Code  
│   ├── dht11.h         # DHT11 Class Declaration  
│   ├── dht11.cpp       # DHT11 Driver Implementation  
│   ├── oled.h          # OLED Class Declaration  
│   ├── oled.cpp        # OLED Driver Implementation  
│   └── main.cpp        # Main Program Logic  
├── scripts/            # Python Scripts  
│   ├── server.py       # Web Server  
│   └── speak.py        # Voice Assistant  
├── sensor_data.json    # Data Storage File  
├── requirements.txt    # Python Dependencies  
└── LICENSE             # License File  
```  

### 2. Core Class Descriptions  
#### DHT11 Class (dht11.h/cpp)  
- **Function**: Encapsulates DHT11 communication and data validation.  
- **Key Methods**:  
  - `readData()`: Returns `std::pair<float, float>` (humidity, temperature), or `std::nullopt` on validation failure.  
  - `pi_mmio_init()`: Initializes GPIO memory mapping for high-speed hardware access.  

#### OLED Class (oled.h/cpp)  
- **Function**: Controls OLED display, supporting text rendering and initialization.  
- **Key Methods**:  
  - `drawText(int page, int col, std::string)`: Draws text at specified page (0-4) and column (0-127).  
  - `init()`: Configures OLED parameters (contrast, scan direction, etc.).  


## 6. Contribution & Collaboration  

### 1. Code Standards  
- **C++**: Follow C++11, camelCase naming (e.g., `drawText`), Doxygen comments for key functions.  
- **Python**: Adhere to PEP8, module-level comments, avoid global variables.  

### 2. Contribution Workflow  
1. Fork the repo and create a feature branch (e.g., `feature/add-bme280`).  
2. Run unit tests (to be added) before code submission.  
3. Submit Pull Requests with feature descriptions and test steps.  

### 3. Issue Reporting  
- **Bug Reports**: Include reproduction steps, hardware model, and error logs (e.g., "dht11.cpp line XX validation failed").  
- **Feature Requests**: Submit via GitHub Issues with "Enhancement" label.  


## 7. License & Acknowledgments  

### License  
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.  

### Acknowledgments  
Thanks to the following open-source projects and communities:  
- [Vosk](https://alphacephei.com/vosk): Speech recognition engine  
- [pyttsx3](https://pyttsx3.readthedocs.io): Text-to-speech library  
- [Flask](https://palletsprojects.com/p/flask/): Web development framework  
- [Raspberry Pi Foundation](https://www.raspberrypi.org/): Hardware documentation and community resources  


## 8. Future Plans  

### Roadmap  
| Version | Timeline | Core Features                          |  
|---------|----------|----------------------------------------|  
| v1.1    | Q1 2024  | Support for BME280 sensor (pressure/altitude) |  
| v1.2    | Q2 2024  | Migrate from JSON to SQLite database    |  
| v1.3    | Q3 2024  | Develop mobile apps (Android/iOS)      |  

### Maintenance  
- Regular dependency updates and security patches (monthly).  
- Bug fixes for community feedback within 72 hours.  
