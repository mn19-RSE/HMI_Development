/*********************************
Created by: Mason Newman
Date: December 2025

Originally written for Raspberry Pi PICO 2W (RP2350)

This sketch was created as a companion to the TFT_GFX_bitmap_test.
The basic function is to read an analog input and send it via UART to the MCU hosting the HMI.
This code serves as the seed for the implemented version of the ammeter P1AM-200 code.
*********************************/


const int maxRaw = 4095;
void setup() {
  Serial.begin(115200);      // USB debug
  Serial1.begin(500000);     // UART0
  analogReadResolution(12);  // 0–4095
  pinMode(26, OUTPUT);
  digitalWrite(26, HIGH);
  pinMode(27, INPUT);
}


void loop() {
  uint16_t adcValue = analogRead(27);
  Serial1.write(0xA5);             // sync
  Serial1.write(adcValue & 0xFF);  // LSB
  Serial1.write(adcValue >> 8);    // MSB
  Serial.println(adcValue);
  delay(20);
}
