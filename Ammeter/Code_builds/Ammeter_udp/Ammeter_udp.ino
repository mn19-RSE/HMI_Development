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


#include <Ethernet.h>
#include <Arduino.h>
#include <EthernetUdp.h>
#include <SPI.h>

const int localPort = 8888;   // Local port to listen on
const int remotePort = 1194;  // Remote port to send to
const int csPin = 17;         // SPI cs pin on W5100s-EVB-PICO

byte mac[] = { 0x02, 0xDE, 0xAD, 0xBE, 0xEF, 0x02 }; 

IPAddress ip(192, 168, 42, 32);        // controller IP 
IPAddress remoteIP(192, 168, 42, 15);  // PC's static IP

EthernetUDP Udp;
//////////////////////////
const int leastBit = 2;
const int middleBit = 3;
const int mostBit  = 4; 
//////////////////////////
const int8_t inputSelection[] = {10, 11, 12, 13, 14, 15, 20, 21, 22, 28};
const int NUM_INPUTS = sizeof(inputSelection) / sizeof(inputSelection[0]);
int activeCup = -1;
//////////////////////////
int rangeSet = -1;
int lastValue = 0;
int lastActiveCup = 0;
unsigned long lastCupPressTime = 0;
const unsigned long debounceDelay = 250;
String currentPrefix = ""; 
//////////////////////////
const int8_t rangeValues[] = {-10, -9, -8, -7, -6, -5, -4, -3, 0};
const int NUM_RANGES = sizeof(rangeValues) / sizeof(rangeValues[0]);
//////////////////////////
enum RxState {WAIT_SYNC, READ_LSB, READ_MSB};
RxState rxState = WAIT_SYNC;
uint8_t lsb;
uint16_t latestADCValue = 0;
float analogVoltage;


void setup() {
  Serial.begin(115200);   // USB debug
  Serial1.begin(500000);  // UART0
  for (int cupPins = 0; cupPins < NUM_INPUTS; cupPins++) {
    pinMode(inputSelection[cupPins], INPUT_PULLUP);
  }
  pinMode(leastBit, INPUT);
  pinMode(middleBit, INPUT);
  pinMode(mostBit, INPUT);

  SPI.begin();  //start SPI
  Ethernet.init(csPin);  // Set CS pin for W5100S-EVB-Pico
  Serial.println("Starting Ethernet connection...");
  Ethernet.begin(mac, ip);  //Initializing ethernet controller buy setting mac address and static ip
  delay(1000);
  Serial.println("Ethernet initialized");
  Serial.print("IP address: ");
  Serial.println(Ethernet.localIP());  // Print the MCU's IP address.
  Serial.print("Subnet mask: ");
  Serial.println(Ethernet.subnetMask());  // Print the MCU's subnet mask.
  Serial.print("Gateway IP: ");
  Serial.println(Ethernet.gatewayIP());  // Print the gateway IP address.
  Serial.print("DNS server IP: ");
  Serial.println(Ethernet.dnsServerIP());  // Print the DNS server IP address.
  Udp.begin(localPort);
  delay(50);
}

void loop() {
  analogVoltage = (handleUARTReceive() * 2000.0f / 8192.0f);
  readInputSelection();
  readRange();
  sendAllData();
}

void sendAllData() {
  Udp.beginPacket(remoteIP, remotePort);
  Udp.print("Input selection: ");
  Udp.print(activeCup);
  Udp.println("  ");
  Udp.print("Range: ");
  Udp.print(rangeSet);
  Udp.println("  ");
  Udp.print("Current value: ");
  Udp.print(analogVoltage);
  Udp.println("  ");
  Udp.print("Current value: ");
  Udp.print(currentPrefix);
  Udp.println("  ");
  Udp.endPacket();
}

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
  return latestADCValue;
}


void readRange() {
  int b0 = digitalRead(leastBit);   // LSB
  int b1 = digitalRead(middleBit);
  int b2 = digitalRead(mostBit);    // MSB
  rangeSet = (b2 << 2) | (b1 << 1) | b0;

  if (rangeSet == 7) {
    currentPrefix = "mA"; // mA
  } else if (rangeSet >= 4) {
    currentPrefix = "µA"; // µA
  } else if (rangeSet >= 0) {
    currentPrefix = "nA"; // nA
  }
}


void readInputSelection() {
  unsigned long now = millis();
  if ((now - lastCupPressTime) >= debounceDelay) {
    activeCup = -1;
    for (int cupPins = 0; cupPins < NUM_INPUTS; cupPins++) {
      if (digitalRead(inputSelection[cupPins]) == LOW) {
        activeCup = cupPins;
        break;
      }
    }
    lastCupPressTime = now;
    lastActiveCup = activeCup;
  }
}
