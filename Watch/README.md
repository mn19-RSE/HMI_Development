# Watch Display Project

## Scope:
The goal of this project is to create a small wearble device with a display. 

## General Outline:
- Small display
    - OLED preffered
        - [NHD-0.95-9664G](https://newhavendisplay.com/content/specs/NHD-0.95-9664G.pdf)
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
    
### PCB Design:
- Switched to using 18650 power
    - Charged off PCB
    - REMOVED 5V USB pin connection
        - Will need battery to upload code
- TPS63060 buck/boost converter for steady 3.3V
    - [TPS63060DSCR](https://www.ti.com/lit/ds/symlink/tps63060.pdf?HQS=dis-dk-null-digikeymode-dsf-pf-null-wwe&ts=1767501359631&ref_url=https%253A%252F%252Fwww.ti.com%252Fgeneral%252Fdocs%252Fsuppproductinfo.tsp%253FdistId%253D10%2526gotoUrl%253Dhttps%253A%252F%252Fwww.ti.com%252Flit%252Fgpn%252Ftps63060)
- OLED soldered directly to PCB
    - No connectors available for 23-pin .7 mm pitch FPC
    - Circuit modeled after Adafruit breakout board design

### Case 3D Design:
- Test prints done to evaluate wrist fit
- Built in 18650 holder

