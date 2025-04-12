#include <iostream>
#include <string>
#include <unistd.h>
#include <fstream>
#include <future>
#include <iomanip>
#include <ctime>
#include <chrono>
#include <vector>
#include "dht11.h"
#include "oled.h"

#define DHT11_PIN 4 // Using GPIO4 with BCM numbering

using namespace std;

void writeSensorData(float temp, float humi)
{
    // 1. Get high-precision timestamp (ensures uniqueness for each call)
    auto now = std::chrono::system_clock::now();
    double timestamp = std::chrono::duration<double>(
                           now.time_since_epoch())
                           .count();

    // 2. Open file and check existing content
    std::fstream file("sensor_data.json", std::ios::in | std::ios::out);
    bool fileExists = file.is_open() && file.peek() != std::ifstream::traits_type::eof();

    // 3. Determine write mode based on file status
    if (fileExists)
    {
        // File exists and is not empty: position before the last ']' to append new data
        file.seekp(-1, std::ios::end);
        char lastChar;
        file.get(lastChar);

        if (lastChar == ']')
        {
            file.seekp(-1, std::ios::end);
            file << ","; // Add comma separator
            file.close();

            // Append new data (fixed decimal format)
            std::ofstream outfile("sensor_data.json", std::ios::app);
            outfile << std::fixed << std::setprecision(6)
                    << "{\"time\":" << timestamp
                    << ", \"temperature\":" << temp
                    << ", \"humidity\":" << humi << "}]";
        }
        else
        {
            // File format error (missing closing ']'), rebuild file
            file.close();
            std::ofstream outfile("sensor_data.json");
            outfile << std::fixed << std::setprecision(6)
                    << "[{\"time\":" << timestamp
                    << ", \"temperature\":" << temp
                    << ", \"humidity\":" << humi << "}]";
        }
    }
    else
    {
        // File doesn't exist or is empty: create new array
        std::ofstream outfile("sensor_data.json");
        outfile << std::fixed << std::setprecision(6)
                << "[{\"time\":" << timestamp
                << ", \"temperature\":" << temp
                << ", \"humidity\":" << humi << "}]";
    }
}

/**
 * speech recognition
 */
void speak()
{
    std::string command = "bash -c 'source /home/pi/dht11_env/bin/activate && python3 /home/pi/temperature-and-humidity-pi/speak.py'";
    std::system(command.c_str());
}

/**
 * server
 */
void server() {
    std::string command = "bash -c 'source /home/pi/dht11_env/bin/activate && python3 /home/pi/temperature-and-humidity-pi/server.py'";
    std::system(command.c_str());
}

int main(void)
{
    OLED oled;
    oled.init();
    oled.clear();
    DHT11 dht(DHT11_PIN);
    // Start voice output thread asynchronously
    std::future<void> speak_future = std::async(std::launch::async, speak);
    std::future<void> server_future = std::async(std::launch::async, server);
    
    while (true)
    {
        auto result = dht.readData();
        if (!result)
        {
            cerr << "Failed to read DHT11 data!" << endl;
            continue; // Skip current iteration
        }
        auto [humidity, temperature] = *result;
        cout << "Temperature: " << temperature << "C" << endl;
        cout << "Humidity: " << humidity << "%" << endl;
        writeSensorData(temperature, humidity);
        
        char tempStr[20];
        char humidityStr[20];

        // Format numbers as strings using sprintf
        sprintf(tempStr, "%.1f", temperature);
        sprintf(humidityStr, "%.1f", humidity);
        
        // Concatenate strings for display
        std::string tempText = "TEMPERATURE: " + std::string(tempStr) + "C";
        std::string humidityText = "HUMIDITY: " + std::string(humidityStr) + "%";
        
        // Get current time
        std::time_t currentTime = std::time(nullptr);
        // Convert to local time
        std::tm *localTime = std::localtime(&currentTime);
        
        // Format time using std::ostringstream
        std::ostringstream oss;
        oss << std::put_time(localTime, "%Y-%m-%d");
        std::string timeText = "TIME: " + oss.str();
        
        // Display text on OLED
        oled.drawText(0, 0, timeText.c_str());
        oled.drawText(2, 0, tempText.c_str()); // .c_str() to get C-style string
        oled.drawText(4, 0, humidityText.c_str());
        
        // Check if thread has completed
        if (speak_future.wait_for(std::chrono::seconds(0)) == std::future_status::ready)
        {
            cout << "Process exited" << endl;
            oled.clear();
            break;
        }
        sleep(60);
        oled.clear();
    }

    return 0;
}