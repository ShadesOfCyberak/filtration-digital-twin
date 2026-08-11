/*
 * ESP32 IoT Sensor Node for Liquid Filtration System
 * Reads differential pressure sensors, flow meter, pump current sensor,
 * and publishes JSON telemetry payloads to Mosquitto MQTT broker over WiFi.
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "config.h"
#include "sensors.h"
#include "mqtt_handler.h"

unsigned long lastPublishTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- ESP32 Filtration Digital Twin Sensor Node Starting ---");

  setupSensors();
  setupWiFi();
  setupMQTT();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  }

  ensureMQTTConnected();
  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastPublishTime >= PUBLISH_INTERVAL_MS) {
    lastPublishTime = now;
    readAndPublishSensors();
  }
}
