/******************************************
Created by: Mason Newman
Date: February 2026

Originally written for WIZNET W5100S-EVB-PICO2 (RP2350)

This sketch was created to send UDP packets containting:
    - Range selection
    - Input selection
    - Analog reading
        - Including polarity
This MCU receives data from the Ammeter_analog MCU and reads digital pins to determine what to send. 
A static IP will be set and a steady stream of packets containing the data will be sent to the SlowDash host PC (192.168.42.15 as of 02/02/2026).
Pins from the selection knob, UART coms, and range enumerator buttons are shared with the Ammeter_display, so the pin assignments hould be identical.
******************************************/









float handleUARTReceive() {
  // Non-blocking and self-aligning UART receive
  while (Serial1.available()) {
    uint8_t b = Serial1.read();
    switch (rxState) {
      case WAIT_SYNC:
        if (b == 0xA5) {
          rxState = READ_LSB;
        }
        break;
      case READ_LSB:
        lsb = b;
        rxState = READ_MSB;
        break;
      case READ_MSB:
        latestADCValue = lsb | (b << 8);
        rxState = WAIT_SYNC;
        break;
    }
  }
  // Debug print SLOWLY
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 50) {
    // Serial.println(latestADCValue);
    lastPrint = millis();
  }
  return latestADCValue;
}
