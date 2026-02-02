/******************************************
Created by: Mason Newman
Date: February 2026

Originally written for Seeed Studio Xiao ESP32S3 Sense

This sketch was written to test displaying dynamic custom numbers on the Adafruit 0.96" color OLED.
The OLED uses a SSD1331 driver board that receives data over SPI.
This is done since not all display driver libraries supoport text the same way.
This will allow for uniform dynamic numeric text aplication accross many HMIs.
The sketch will outline:
    - How to create and display numbers using hardware accelerated shapes
******************************************/


#include <Adafruit_GFX.h>
#include <Adafruit_SSD1331.h>
#include <SPI.h>

#define show endWrite
#define clear() fillScreen(0)  // not sure what this is yet

// User customizable OLED pin mapping
// Pi Pico 2W:
// OC: GP15
// RST: GP14
// DC: GP13
// Xiao ESP32S3 (use GPIO numbers)
// OC: D6, GPIO43
// RST: D7, GPIO44
// DC: D5, GPIO6
#define cs 43
#define rst 44
#define dc 6
Adafruit_SSD1331 display = Adafruit_SSD1331(&SPI, cs, dc, rst);

const int screenWidth = 96;
const int screenHeight = 64;

void setup() {
  Serial.begin(115200);
  display.begin();  // Default is 40Mhz
  display.setTextWrap(false);
  display.setAddrWindow(0, 0, screenWidth, screenHeight);  // Setting screen size
  display.fillScreen(0xfafa);
  display.show();
  delay(1000);
  display.clear();
  display.setRotation(2);
  Serial.println("display init done");
  delay(1000);
  display.clear();
}

int i = 0;
const int maxNum = 199;
const int countDelay = 50;
int direction = 1;
const int longEdge = 14;
const int shortEdge = 6;
const int digitSpacing = longEdge + shortEdge;
const int radius = shortEdge / 2;

void loop() {
  drawInt3Digits(i, screenWidth - shortEdge - longEdge, shortEdge, 0x320d);
  i += direction;

  if (i >= maxNum) {
    i = maxNum;
    direction = -1;
  }

  if (i <= -maxNum) {
    i = -maxNum;
    direction = 1;
  }
  delay(countDelay);
}


void drawInt3Digits(int value, int baseX, int baseY, uint16_t color) {
  display.fillRect(baseX - (2 * digitSpacing) - (shortEdge * 2), baseY, (longEdge * 3) + (shortEdge * 3), (longEdge * 2) - shortEdge, 0x0000);  //clear digit area
  display.fillRoundRect(baseX - longEdge - (shortEdge * 3), baseY + (longEdge * 2) - (shortEdge * 2), shortEdge, shortEdge, radius, color);                  // draw decimal point
  int minusX = baseX - (digitSpacing * 3) - (shortEdge * 2);
  int minusW = longEdge;

  int minusY = baseY + longEdge - shortEdge;
  int minusH = shortEdge;

  int plusBarX = minusX + (minusW / 2) - (shortEdge / 2);
  int plusBarY = baseY + (longEdge / 2) - (shortEdge / 2);
  int plusBarH = longEdge;

  if (value >= 0) {
    display.fillRoundRect(plusBarX, plusBarY, shortEdge, plusBarH, radius, color);  // vertical bar (+)
  } else {
    display.fillRoundRect(plusBarX, plusBarY, shortEdge, plusBarH, radius, 0x0000);
  }

  display.fillRoundRect(minusX, minusY, minusW, minusH, radius, color);  // minus sign

  value = abs(value);
  value = constrain(value, 0, 999);

  // Extract digits
  int ones = value % 10;
  int tens = (value / 10) % 10;
  int hundreds = (value / 100) % 10;


  drawNumber(ones, baseX, baseY, color);
  if (value < 10) {
    drawNumber(0, baseX - digitSpacing, baseY, color);
    drawNumber(0, baseX - (digitSpacing * 2) - (shortEdge * 2), baseY, color);
  }

  if (value >= 10 && value < 100) {
    drawNumber(tens, baseX - digitSpacing, baseY, color);
    drawNumber(0, baseX - (digitSpacing * 2) - (shortEdge * 2), baseY, color);
  }

  if (value >= 100) {
    drawNumber(tens, baseX - digitSpacing, baseY, color);
    drawNumber(hundreds, baseX - (digitSpacing * 2) - (shortEdge * 2), baseY, color);
  }
}

void drawNumber(int numberDraw, int numXLoc, int numYLoc, uint16_t numColor) {
  // 1 = b, c
  // 2 = a, b, d, e, g
  // 3 = a, b, c, d, g
  // 4 = b, c, f, g
  // 5 = a, c, d, f, g
  // 6 = a, c, d, e, f, g
  // 7 = a, b, c
  // 8 = a, b, c, d, e, f, g
  // 9 = a, b, c, d, f, g
  // 0 = a, b, c, d, e, f
  if (numberDraw == 1) {
    // display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);   // a
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);                         // b
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);  // c
    // display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);   // d
    // display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);   // e
    // display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);   // f
    // display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);   // g
  }
  if (numberDraw == 2) {
    display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);                         // a
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);  // b
    // display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge -shortEdge, shortEdge, longEdge, radius, numColor);   // c
    display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);  // d
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);              // e
    // display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);   // f
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);  // g
  }
  if (numberDraw == 3) {
    display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);                                                // a
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);                         // b
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);  // c
    display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);             // d
    // display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);   // e
    // display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);   // f
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);  // g
  }
  if (numberDraw == 4) {
    // display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);   // a
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);                         // b
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);  // c
    // display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);   // d
    // display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);   // e
    display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);                         // f
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);  // g
  }
  if (numberDraw == 5) {
    display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);  // a
    // display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);   // b
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);  // c
    display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);             // d
    // display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);   // e
    display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);                         // f
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);  // g
  }
  if (numberDraw == 6) {
    display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);  // a
    // display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);   // b
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);  // c
    display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);             // d
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);                         // e
    display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);                                                // f
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);                         // g
  }
  if (numberDraw == 7) {
    display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);                                                // a
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);                         // b
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);  // c
    // display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);   // d
    // display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);   // e
    // display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);   // f
    // display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);   // g
  }
  if (numberDraw == 8) {
    display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);                                                // a
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);                         // b
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);  // c
    display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);             // d
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);                         // e
    display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);                                                // f
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);                         // g
  }
  if (numberDraw == 9) {
    display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);                                                // a
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);                         // b
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);  // c
    display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);             // d
    // display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);   // e
    display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);                         // f
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);  // g
  }
  if (numberDraw == 0) {
    display.fillRoundRect(numXLoc, numYLoc, longEdge, shortEdge, radius, numColor);                                                // a
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc, shortEdge, longEdge, radius, numColor);                         // b
    display.fillRoundRect(numXLoc + longEdge - shortEdge, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);  // c
    display.fillRoundRect(numXLoc, numYLoc + (longEdge * 2) - (shortEdge * 2), longEdge, shortEdge, radius, numColor);             // d
    display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, shortEdge, longEdge, radius, numColor);                         // e
    display.fillRoundRect(numXLoc, numYLoc, shortEdge, longEdge, radius, numColor);                                                // f
    // display.fillRoundRect(numXLoc, numYLoc + longEdge - shortEdge, longEdge, shortEdge, radius, numColor);   // g
  }
}