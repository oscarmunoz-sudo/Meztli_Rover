#include <Arduino.h>

#define RXD2 16
#define TXD2 17

void setup() {

  // USB hacia PC
  Serial.begin(115200);

  // UART hacia TL725D
  Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);

  Serial.println("ESP32 IMU bridge iniciado");
}

void loop() {

  // datos del sensor → PC
  while (Serial2.available()) {
    Serial.write(Serial2.read());
  }

  // opcional: PC → sensor
  while (Serial.available()) {
    Serial2.write(Serial.read());
  }
}