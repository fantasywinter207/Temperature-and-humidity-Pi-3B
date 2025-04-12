#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <errno.h>
#include <sched.h>
#include <sys/time.h>
#include <time.h>
#include <iostream>
#include <optional>

#include "dht11.h"

// Base address for memory mapping
#define BASE 0x20000000
// GPIO base address relative to BASE
#define GPIO_BASE (BASE + 0x200000)
// Length of the GPIO memory region to map
#define GPIO_LENGTH 4096

// Success code for memory mapping initialization
#define MMIO_SUCCESS 0
// Error code when opening /dev/gpiomem or /dev/mem fails
#define MMIO_ERROR_DEVMEM -1
// Error code when memory mapping fails
#define MMIO_ERROR_MMAP -2

// Maximum number of counts for waiting on DHT pulses
#define DHT_MAXCOUNT 32000
// Number of DHT pulses to read
#define DHT_PULSES 41

// Constructor for DHT11 class, initializes the GPIO pin number
DHT11::DHT11(int pin) : pin_(pin), pi_mmio_gpio(nullptr) {}

// Destructor for DHT11 class
DHT11::~DHT11() {}

// Initialize memory mapping for GPIO access
// Returns MMIO_SUCCESS on success, MMIO_ERROR_DEVMEM or MMIO_ERROR_MMAP on failure
int DHT11::pi_mmio_init() {
    if (pi_mmio_gpio == nullptr) {
        int fd;

        // /dev/gpiomem may not exist on older kernels, fall back to /dev/mem (root access required)
        if (access("/dev/gpiomem", F_OK) != -1) {
            fd = open("/dev/gpiomem", O_RDWR | O_SYNC);
        } else {
            fd = open("/dev/mem", O_RDWR | O_SYNC);
        }
        if (fd == -1) {
            // Failed to open /dev/gpiomem or /dev/mem
            return MMIO_ERROR_DEVMEM;
        }
        // Map the GPIO memory region to the process's address space
        pi_mmio_gpio = (uint32_t*)mmap(nullptr, GPIO_LENGTH, PROT_READ | PROT_WRITE, MAP_SHARED, fd, GPIO_BASE);
        close(fd);
        if (pi_mmio_gpio == MAP_FAILED) {
            // Memory mapping failed, do not save the result
            pi_mmio_gpio = nullptr;
            return MMIO_ERROR_MMAP;
        }
    }
    return MMIO_SUCCESS;
}

// Busy wait for a specified number of milliseconds
// This method has high CPU usage but provides precise timing for short durations (up to a few hundred milliseconds)
void DHT11::busy_wait_milliseconds(uint32_t millis) {
    // Set the delay period
    struct timeval deltatime;
    deltatime.tv_sec = millis / 1000;
    deltatime.tv_usec = (millis % 1000) * 1000;
    struct timeval walltime;
    // Get the current time and add the delay to find the end time
    gettimeofday(&walltime, nullptr);
    struct timeval endtime;
    timeradd(&walltime, &deltatime, &endtime);
    // Tight loop to waste time (and CPU) until enough time has passed
    while (timercmp(&walltime, &endtime, <)) {
        gettimeofday(&walltime, nullptr);
    }
}

// Sleep for a specified number of milliseconds
// This method has low CPU usage but may have lower accuracy
void DHT11::sleep_milliseconds(uint32_t millis) {
    struct timespec sleep;
    sleep.tv_sec = millis / 1000;
    sleep.tv_nsec = (millis % 1000) * 1000000L;
    while (clock_nanosleep(CLOCK_MONOTONIC, 0, &sleep, &sleep) && errno == EINTR);
}

// Set the process to the maximum priority using the FIFO scheduler
// This attempts to achieve "real-time" behavior by reducing kernel context switches
void DHT11::set_max_priority() {
    struct sched_param sched;
    memset(&sched, 0, sizeof(sched));
    // Use the FIFO scheduler with the highest priority
    sched.sched_priority = sched_get_priority_max(SCHED_FIFO);
    sched_setscheduler(0, SCHED_FIFO, &sched);
}

// Set the process back to the default priority and scheduler
void DHT11::set_default_priority() {
    struct sched_param sched;
    memset(&sched, 0, sizeof(sched));
    // Return to the default scheduler with priority 0
    sched.sched_priority = 0;
    sched_setscheduler(0, SCHED_OTHER, &sched);
}

// Read temperature and humidity data from the DHT sensor
// Returns a std::pair containing humidity and temperature if successful, std::nullopt otherwise
std::optional<std::pair<float, float>> DHT11::readData() {
    float humidity = 0.0f;
    float temperature = 0.0f;

    // Initialize the GPIO library
    if (pi_mmio_init() < 0) {
        return std::nullopt;
    }

    // Array to store the low and high pulse counts for each DHT bit
    // Ensure the array is initialized to zero
    int pulseCounts[DHT_PULSES * 2] = {0};

    // Set the GPIO pin to output mode
    pi_mmio_set_output(pin_);

    // Increase the process priority and change the scheduler to attempt "real-time" behavior
    set_max_priority();

    // Set the pin high for approximately 500 milliseconds
    pi_mmio_set_high(pin_);
    sleep_milliseconds(500);

    // The following calls are time-critical, ensure there is no unnecessary work below

    // Set the pin low for approximately 20 milliseconds
    pi_mmio_set_low(pin_);
    busy_wait_milliseconds(20);

    // Set the pin to input mode
    pi_mmio_set_input(pin_);
    // A very short delay is required before reading the pin, otherwise the value may still be low
    for (volatile int i = 0; i < 500; ++i) {
    }

    // Wait for the DHT to pull the pin low
    uint32_t count = 0;
    while (pi_mmio_input(pin_)) {
        if (++count >= DHT_MAXCOUNT) {
            // Timed out waiting for response
            set_default_priority();
            return std::nullopt;
        }
    }

    // Record the pulse widths for the expected result bits
    for (int i = 0; i < DHT_PULSES * 2; i += 2) {
        // Count the duration of the low pulse and store it in pulseCounts[i]
        while (!pi_mmio_input(pin_)) {
            if (++pulseCounts[i] >= DHT_MAXCOUNT) {
                // Timed out waiting for response
                set_default_priority();
                return std::nullopt;
            }
        }
        // Count the duration of the high pulse and store it in pulseCounts[i + 1]
        while (pi_mmio_input(pin_)) {
            if (++pulseCounts[i + 1] >= DHT_MAXCOUNT) {
                // Timed out waiting for response
                set_default_priority();
                return std::nullopt;
            }
        }
    }

    // Finished time-critical code, now interpret the results

    // Restore to normal priority
    set_default_priority();

    // Calculate the average low pulse width as a reference threshold for 50 microseconds
    // Ignore the first two readings as they are constant 80 microsecond pulses
    uint32_t threshold = 0;
    for (int i = 2; i < DHT_PULSES * 2; i += 2) {
        threshold += pulseCounts[i];
    }
    threshold /= DHT_PULSES - 1;

    // Interpret each high pulse as a 0 or 1 by comparing it to the 50 microsecond reference value
    // If the count is less than 50 microseconds, it must be a 0 pulse (approximately 28 microseconds),
    // if higher, it must be a 1 pulse (approximately 70 microseconds)
    uint8_t data[5] = {0};
    for (int i = 3; i < DHT_PULSES * 2; i += 2) {
        int index = (i - 3) / 16;
        data[index] <<= 1;
        if (pulseCounts[i] >= threshold) {
            // Long pulse indicates a 1 bit
            data[index] |= 1;
        }
        // Short pulse indicates a 0 bit
    }

    // Verify the checksum of the received data
    if (data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF)) {
        humidity = static_cast<float>(data[0]);
        temperature = static_cast<float>(data[2]);
        return std::pair(humidity, temperature);
    } else {
        return std::nullopt;
    }
}

// Set the specified GPIO pin to input mode
void DHT11::pi_mmio_set_input(const int gpio_number) {
    // Set the GPIO register for the specified GPIO number to 000
    *(pi_mmio_gpio + ((gpio_number) / 10)) &= ~(7 << (((gpio_number) % 10) * 3));
}

// Set the specified GPIO pin to output mode
void DHT11::pi_mmio_set_output(const int gpio_number) {
    // First set it to 000 using the input function
    pi_mmio_set_input(gpio_number);
    // Then set bit 0 to 1 to set it to output
    *(pi_mmio_gpio + ((gpio_number) / 10)) |= (1 << (((gpio_number) % 10) * 3));
}

// Set the specified GPIO pin high
void DHT11::pi_mmio_set_high(const int gpio_number) {
    *(pi_mmio_gpio + 7) = 1 << gpio_number;
}

// Set the specified GPIO pin low
void DHT11::pi_mmio_set_low(const int gpio_number) {
    *(pi_mmio_gpio + 10) = 1 << gpio_number;
}

// Read the input value of the specified GPIO pin
uint32_t DHT11::pi_mmio_input(const int gpio_number) {
    return *(pi_mmio_gpio + 13) & (1 << gpio_number);
}