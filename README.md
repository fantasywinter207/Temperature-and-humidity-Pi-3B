# Real-Time Environmental Monitoring System for Raspberry Pi

![Project Image](path/to/your/project/image.png)

**Revolutionize your environmental monitoring with our cutting - edge Raspberry Pi system!**

This embedded system, designed specifically for Raspberry Pi, integrates real - time temperature and humidity monitoring, OLED data display, data storage, and voice interaction. Ideal for smart homes, greenhouses, and small - scale industrial monitoring.

[Click here to watch our project in action!](https://youtu.be/6Cy_jflKvcY?si=Tw9HrwRCOWop9JV1)

## 1. Project Overview
### Project Name
Real-Time Environmental Monitoring System for Raspberry Pi

### Project Description
An embedded system developed for Raspberry Pi, integrating temperature/humidity monitoring, OLED data display, data storage, and voice interaction. Suitable for smart homes, greenhouses, and small - scale industrial monitoring. Uses C++ for hardware drivers and Python for web services and voice functions, balancing performance and development efficiency.

### Core Advantages
- **Realtime Performance**: Thread prioritization and multi - threading ensure non - blocking sensor data collection and interface refresh.
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

![OLED Display Screenshot](images/5.jpg)

### 3. Data Storage & Web API  
- **Local Storage**:  
  - Data stored in `sensor_data.json` (JSON format), retaining up to 1000 historical records.  
  - Includes timestamp, temperature, and humidity fields, supporting resume on breakpoint and file recovery.  
- **Web Services**:  
  - Flask-based RESTful API:  
    - **POST /data**: Upload real-time data (Content-Type: application/json).  
    - **GET /data**: Retrieve historical data for frontend display or analysis.

![Web Interface Screenshot](images/6.png)

### 4. Voice Interaction System  
- **Speech Recognition**:  
  - Wake word "computer" activates the system, supporting English/Chinese commands.  
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

![Hardware Connection Diagram](images/7.png)

### 2. Software Architecture  
```  
Raspberry Pi OS (Raspbian)  
├─ C++ Hardware Driver Layer  
│  ├─ DHT11 Class (dht11.h/cpp): Sensor communication and data validation  
│  └─ OLED Class (oled.h/cpp): I2C protocol and text rendering  
├─ Python Service Layer  
│  ├─ Flask Web Server (server.py): Data storage and API  
│  └─ Web(index.html/web): Web and voice modules
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

![DHT11 Wiring Diagram](images/3.jpg)
![OLED Wiring Diagram](images/1.jpg)

### 2. Software Installation  
#### Step 1: Clone Repository  
```bash  
git clone https://github.com/fantasywinter207/Temperature-and-humidity-Pi-3B.git  
cd Temperature-and-humidity-Pi-3B 
```  

### 3. System Startup Commands  
```bash
bash ./run.sh
```

### 4. Voice Command List
| Command Type   | Example Command         | System Response                     |
|----------------|-------------------------|-------------------------------------|
| Wake Command   | "computer"              | "How can I help you?"               |
| Temp/Humid Query| "Humidity" or "temperature"| "Current temperature is 25.5°C"     |
| Time Query     | "time"      | "The current time is 14:30"         |
| Exit Command   | "exit" or "quit"                 | "Goodbye!" (stops all services)     |

## 5. Code Structure & Module Description
### 1. Directory Structure
```
Project Root
├── dht11.h         # DHT11 Class Declaration
├── dht11.cpp       # DHT11 Driver Implementation
├── oled.h          # OLED Class Declaration
├── oled.cpp        # OLED Driver Implementation
├── main.cpp        # Main Program Logic
├── server.py       # Web Server
├── sensor_data.json    # Data Storage File
├── requirements.txt    # Python Dependencies
├── templates/      # HTML templates
│   └── index.html  # Front - end page
├── run.sh          # Script to compile and run the program
├── .github/        # GitHub Actions configuration
│   └── workflows/
│       └── c - cpp.yml # C/C++ CI configuration
└── LICENSE         # License File
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
  - `drawText(int page, int col, std::string)`: Draws text at specified page (0 - 4) and column (0 - 127).
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
- [pyttsx3](https://pyttsx3.readthedocs.io): Text-to-speech library
- [Flask](https://palletsprojects.com/p/flask/): Web development framework
- [Raspberry Pi Foundation](https://www.raspberrypi.org/): Hardware documentation and community resources

## 8. Future Plans
### Maintenance
- Regular dependency updates and security patches (monthly).
- Bug fixes for community feedback within 72 hours.

### Roadmap
| Version | Timeline | Core Features                          |
|---------|----------|----------------------------------------|
| v1.1    | Q1 2025  | Support for BME280 sensor (pressure/altitude) |
| v1.2    | Q2 2025  | Migrate from JSON to SQLite database    |
| v1.3    | Q3 2025  | Develop mobile apps (Android/iOS)      |
