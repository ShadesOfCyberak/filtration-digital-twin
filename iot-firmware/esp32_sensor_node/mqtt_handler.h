#ifndef MQTT_HANDLER_H
#define MQTT_HANDLER_H

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "config.h"
#include "sensors.h"

WiFiClient espClient;
PubSubClient mqttClient(espClient);

void setupWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 10) {
    delay(500);
    Serial.print(".");
    tries++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected! IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\nWiFi Connection failed. Running standalone.");
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived on topic [");
  Serial.print(topic);
  Serial.print("]: ");
  
  StaticJsonDocument<256> doc;
  deserializeJson(doc, payload, length);
  const char* command = doc["command"];

  if (String(command) == "backwash") {
    int durationSec = doc["parameters"]["duration_seconds"] | 30;
    Serial.printf("Triggering Backwash Relay for %d seconds\n", durationSec);
    digitalWrite(PIN_RELAY_BACKWASH, HIGH);
    delay(durationSec * 1000);
    digitalWrite(PIN_RELAY_BACKWASH, LOW);
    Serial.println("Backwash cycle completed.");
  }
}

void setupMQTT() {
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
}

void ensureMQTTConnected() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqttClient.connect(DEVICE_ID)) {
      Serial.println("Connected to Broker!");
      mqttClient.subscribe(TOPIC_CONTROL);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retrying in 2 seconds...");
      delay(2000);
      break;
    }
  }
}

void publishMetric(const char* topic, const char* sensorId, float value, const char* unit) {
  StaticJsonDocument<200> doc;
  doc["device_id"] = DEVICE_ID;
  doc["sensor_id"] = sensorId;
  doc["value"] = value;
  doc["unit"] = unit;
  doc["quality"] = "good";

  char buffer[256];
  serializeJson(doc, buffer);
  mqttClient.publish(topic, buffer);
}

void readAndPublishSensors() {
  float p_in = readPressureInlet();
  float p_out = readPressureOutlet();
  float flow = readFlowRate();
  float curr = readPumpCurrent();

  publishMetric(TOPIC_PRESSURE_INLET, "pressure_inlet", p_in, "bar");
  publishMetric(TOPIC_PRESSURE_OUTLET, "pressure_outlet", p_out, "bar");
  publishMetric(TOPIC_FLOW, "flow", flow, "L/min");
  publishMetric(TOPIC_CURRENT, "current", curr, "A");
}

#endif
