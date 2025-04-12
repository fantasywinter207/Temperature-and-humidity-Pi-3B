#ifndef OLED_H
#define OLED_H

#include <cstdint>
#include <string>

class OLED {
public:
    OLED();
    ~OLED();

    void init();
    void clear();
    void drawChar(char c);
    void drawText(int page, int col, const std::string& str);

private:
    struct gpiod_line* sda;
    struct gpiod_line* scl;
    struct gpiod_chip* chip;

    void i2cDelay();
    void setLine(gpiod_line* line, int value);
    int  readLine(gpiod_line* line);
    void i2cStart();
    void i2cStop();
    bool i2cWriteByte(uint8_t data);
    bool i2cWriteBytes(const uint8_t* data, int length);
    void command(uint8_t cmd);
    void data(uint8_t data);

    static constexpr uint8_t SDA_LINE = 2;  // GPIO02 (BCM)
    static constexpr uint8_t SCL_LINE = 3;  // GPIO03 (BCM)
    static constexpr const char* CHIP_NAME = "gpiochip0";

    static const uint8_t font5x8[][5];
};

#endif // OLED_H