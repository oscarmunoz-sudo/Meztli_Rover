#include <Arduino.h>

void setup() {

  // USB hacia PC
  Serial.begin(115200);
  while (!Serial); // espera conexión USB (opcional pero recomendado)

  // UART hacia TL725D (pines 0 y 1)
  Serial1.begin(115200);

  Serial.println("Nano 33 IoT IMU bridge iniciado");
}

void loop() {

  // datos del sensor → PC
  while (Serial1.available()) {
    Serial.write(Serial1.read());
  }

  // opcional: PC → sensor
  while (Serial.available()) {
    Serial1.write(Serial.read());
  }
}