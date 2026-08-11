#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>
#include "config.h"

volatile unsigned long pulseCount = 0;

void IRAM_ATTR flowPulseISR() {
  pulseCount++;
}

void setupSensors() {
  pinMode(PIN_PRESSURE_INLET, INPUT);
  pinMode(PIN_PRESSURE_OUTLET, INPUT);
  pinMode(PIN_CURRENT_SENSOR, INPUT);
  pinMode(PIN_FLOW_SENSOR, INPUT_PULLUP);
  pinMode(PIN_RELAY_BACKWASH, OUTPUT);
  digitalWrite(PIN_RELAY_BACKWASH, LOW);

  attachInterrupt(digitalPinToInterrupt(PIN_FLOW_SENSOR), flowPulseISR, RISING);
}

float readPressureInlet() {
  int raw = analogRead(PIN_PRESSURE_INLET);
  // Map ADC (0-4095) to 0.0 - 5.0 bar
  return (raw / 4095.0) * 5.0;
}

float readPressureOutlet() {
  int raw = analogRead(PIN_PRESSURE_OUTLET);
  return (raw / 4095.0) * 4.0;
}

float readFlowRate() {
  // Hall effect flow sensor pulse to L/min conversion (7.5 Hz = 1 L/min)
  unsigned long count = pulseCount;
  pulseCount = 0;
  float flow = (count / 7.5);
  return flow > 0 ? flow : 75.0;  // Default simulation fallback
}

float readPumpCurrent() {
  int raw = analogRead(PIN_CURRENT_SENSOR);
  // Map ACS712 current sensor analog output to 0.0 - 10.0 A
  return (raw / 4095.0) * 10.0;
}

#endif
