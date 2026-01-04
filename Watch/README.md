# Watch Display Project

## Scope:
The goal of this project is to create a small wearble device with a display. 

## General Outline:
- Small display
    - OLED preffered
        - [UG-9664HDDAG01](https://cdn-shop.adafruit.com/datasheets/UG-9664HDDAG01.pdf)
            - SPI OLED with on-board [SSD1331 driver](https://cdn-shop.adafruit.com/datasheets/SSD1331_1.2.pdf)
- Battery powered
    - Rechargable
        - [LiPo charger board](https://www.sparkfun.com/sparkfun-lipo-charger-plus.html)
- IMU for gestures
- ESP32 microcontroller
    - ESP32-S3-WROOM-1-N16R8
        - SPI pins for OLED
        - | Pin Name | SPI Function | 
          |----------|--------------|
          | IO10     | Default CS   |
          | IO11     | MOSI         |
          | IO12     | SCK          |
          | IO13     | MISO         |
    - Exposed I2C port for scanner functionality
        - | Pin Name | I2C Function | 
          |----------|--------------|
          | IO8      | SCL          |
          | IO9      | SDA          |
    
