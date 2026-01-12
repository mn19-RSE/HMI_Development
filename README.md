# HMI_Development

## Purpose:
This repo is a collection of files used to learn and develop graphical HMIs, dashboards and other GUIs. This project started with the development of the faraday cup picoammeter for the CENPA VDG controls upgrade project. The general scope is to learn how to design and display interesting and informative graphics on displays using microcontrollers. The first iteration of an HMI uses a 40-pin TFT LCD display that can be driven by a RA8775 board (supplied by [Adafruit](https://www.adafruit.com/product/1590)) and controlled by a RP2350 based MCU. The graphics were designed with Inkscape, an open source vector graphics editor. In the future exploration to other microcontrollers is desirable. The ESP32-P4 has onboard MIPI DSI for driving larger displays. The Waveshare module has the potential to be a well-suited HMI controller.

### Hardware for Evaluation
To summarize the current options for HMI development hardware are:
- ESP32-P4 using DSI output
    - New -> less documented
    - Larger 10-12" displays available
- RP2350 using HSTX to HDMI adapter
    - Up to 640x480  
    - Only Python support
- Any powerful MCU using a SPI display controller (RA8775)
    - Current development logged in [Ammeter](/Ammeter/)
    - Up to 800x480 7.0" TFT LCD
- RP2040 PicoVison
    - Twin RP2040 
    - Runs Python 
- Raspberry Pi
    - Kiosk mode
    - Python based 

## Development Steps:
1. Design graphics in Inkscape with predetermined screen resolution
2. Output background and sprites as individual .PNG
3. ~~Convert .PNG to .BMP with specific pixel width and height~~
4. Convert ~~.BMP~~ .PNG to C array 
    - Specify pixel width and height
    - Select 16-bit RRRRRGGGGGGBBBBB (2byte/pixel)
5. Copy C array to HMI controller software

## Prototypes:
### <img src="Ammeter/mini-tft_demo.jpeg" alt="Mini-TFT Ammeter HMI Steup" width= 50%>
### <img src="Ammeter/large-tft_demo.png" alt="Large TFT Ammeter HMI Setup" width= 50%>

## Links:
### Software:
- [Inkscape](https://inkscape.org/)
- [GIMP](https://www.gimp.org/)
- [Ardhuno IDE](https://www.arduino.cc/en/software/)

### Online Tools:
- [SVG to BMP Converter](https://www.freeconvert.com/svg-to-bmp) (10 Free conversions per day.)
- [SVG to BMP Converter](https://cloudconvert.com/png-to-bmp) (10 Free conversions per day.)
- [SVG to BMP Converter](https://image.online-convert.com/convert-to-bmp) (No limit, only 3 at a time.)
- [Image to C-Array Converter](https://notisrac.github.io/FileToCArray/)

### Libraries:
- [Adafruit GFX](https://github.com/adafruit/Adafruit-GFX-Library)
- [Adafruit RA8875](https://github.com/adafruit/Adafruit_RA8875)
- [Adafruit ST7735](https://github.com/adafruit/Adafruit-ST7735-Library?tab=readme-ov-file)

### Hardware:
- [Adafruit RA8875 40-Pin TFT Driver](https://www.adafruit.com/product/1590)
    - Features hardware-accelerated shapes such as lines, rectangles, triangles, ellipses, built in and round-rects. There is also a built in English/European font set (see the [datasheet section 7-4-1](Ammeter/RA8875_Datasheet.pdf) for the font table) This makes it possible to draw fast even over SPI.
- [Adafruit 1.44" TFT LCD](https://www.adafruit.com/product/2088)
- [Waveshare ESP32-P4-Nano Board WIKI](https://www.waveshare.com/wiki/ESP32-P4-Nano-StartPage#Run_the_First_Arduino_Demo)
    - ESP32-P4 board with MIPI DSI and CSI, also has onboard RJ45 ethernet
- [Pimoroni PicoVision Product Page](https://shop.pimoroni.com/products/picovision?variant=41048911904851)
    - Board with one RP2040 acting as CPU and another RP2040 acting as GPU designed for DVI over HDMI
- [Adafruit FruitJam Product Page](https://www.adafruit.com/product/6200)
    - RP2350 based MCU with DVI over HDMI though HSTX port


## Learning Resources:
[Espressif MIPI DSI Detailed Guide](https://docs.espressif.com/projects/esp-iot-solution/en/latest/display/lcd/mipi_dsi_lcd.html)<br>

