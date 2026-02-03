/******************************************
Created by: Mason Newman
Date: February 2026

Originally written for ProductivityOpen P1AM-200 PLC

This sketch was created to read the -10V to +10V analog output from the Keithley 18000-20 current amplifier.
This PLC has a module speicifically designed to read that voltage range. 
This code will also set the analog output from 0-10V for the panel meter and 0-5V for the remote meter.
This will be the lightest code to keep it as fast as possible since the PLC has a lower clock speed than the Ammeter_display and Ammeter_udp MCUs.
******************************************/


const int maxRaw = 4095;
const int displayMCUReady = 2;
void setup() {
  Serial.begin(115200);      // USB debug
  Serial1.begin(500000);     // UART0
  analogReadResolution(12);  // 0–4095
  pinMode(26, OUTPUT);  // for pot
  digitalWrite(26, HIGH); // for pot
  pinMode(displayMCUReady, INPUT);  // from diaplay MCU 
  pinMode(27, INPUT);  // analog read pin
}


void loop() {
  while (digitalRead(displayMCUReady) == HIGH) {
    uint16_t adcValue = analogRead(27);
    Serial1.write(0xA5);             // sync
    Serial1.write(adcValue & 0xFF);  // LSB
    Serial1.write(adcValue >> 8);    // MSB
    Serial.println(adcValue);
    delay(20);
  }
}