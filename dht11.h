#ifndef COMMON_DHT_H
#define COMMON_DHT_H

#include <cstdint>
#include <optional>

class DHT11 {
public:
    // Constructor: initializes DHT11 sensor on specified GPIO pin
    // @param pin: GPIO pin number connected to the DHT11 data line
    DHT11(int pin);
    
    // Destructor: cleans up resources
    ~DHT11();

    // Reads temperature and humidity data from DHT11 sensor
    // @return: optional pair containing (temperature, humidity) if read is successful,
    //          empty optional if read fails
    std::optional<std::pair<float, float>> readData();

private:
    int pin_;                       // GPIO pin number connected to DHT11
    volatile uint32_t* pi_mmio_gpio; // Pointer to memory-mapped GPIO registers

    // Initializes memory-mapped GPIO interface
    // @return: 0 on success, -1 on failure
    int pi_mmio_init();

    // Busy-wait for specified milliseconds (blocking delay)
    // @param millis: delay duration in milliseconds
    void busy_wait_milliseconds(uint32_t millis);

    // Sleep for specified milliseconds (non-blocking delay)
    // @param millis: sleep duration in milliseconds
    void sleep_milliseconds(uint32_t millis);

    // Set thread to maximum priority for timing-critical operations
    void set_max_priority();

    // Restore thread to default priority
    void set_default_priority();

    // GPIO control functions

    // Sets specified GPIO pin as input
    // @param gpio_number: GPIO pin number to configure
    void pi_mmio_set_input(const int gpio_number);

    // Sets specified GPIO pin as output
    // @param gpio_number: GPIO pin number to configure
    void pi_mmio_set_output(const int gpio_number);

    // Sets specified GPIO pin to high state
    // @param gpio_number: GPIO pin number to set
    void pi_mmio_set_high(const int gpio_number);

    // Sets specified GPIO pin to low state
    // @param gpio_number: GPIO pin number to set
    void pi_mmio_set_low(const int gpio_number);

    // Reads current state of specified GPIO pin
    // @param gpio_number: GPIO pin number to read
    // @return: current state of the GPIO pin (0 or 1)
    uint32_t pi_mmio_input(const int gpio_number);
};

#endif