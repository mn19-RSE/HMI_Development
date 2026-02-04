/******************************************
Created by: Mason Newman
Date: February 2026

Originally written for ProductivityOpen P1AM-200 PLC

This sketch was created to read the -10V to +10V analog output from the Keithley 18000-20 current amplifier.
This PLC has a module speicifically designed to read that voltage range. 
This code will also set the analog output from 0-10V for the panel meter and 0-5V for the remote meter.
This will be the lightest code to keep it as fast as possible since the PLC has a lower clock speed than the Ammeter_display and Ammeter_udp MCUs.
******************************************/

#include <P1AM.h>

// UART pins:
// 14 = TX
// 13 = RX
const int displayMCUReady = 13; // Using the unused RX pin seems to work
void setup() {
  Serial.begin(115200);   // USB debug
  pinMode(displayMCUReady, INPUT);  // from diaplay MCU
  Serial1.begin(500000);  // UART0
  P1.init();
}


void loop() {
  while (digitalRead(displayMCUReady) == HIGH) {
    uint16_t adcValue = P1.readAnalog(1, 1); //slot 1 channel 2;
    Serial.println(adcValue);
    Serial1.write(0xA5);             // sync
    Serial1.write(adcValue & 0xFF);  // LSB
    Serial1.write(adcValue >> 8);    // MSB
    Serial.println(adcValue);
    delay(10);
    // P1.writeAnalog(adcValue, 2, 1); // // Need to correct scaling to 0-10V
    // P1.writeAnalog(adcValue / 2, 2, 2); // Need to correct scaling to 0-5V
  }
  Serial.println("Waiting for Ready");
  delay(500);
}