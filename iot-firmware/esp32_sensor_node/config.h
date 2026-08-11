#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// MQTT Configuration
#define MQTT_BROKER "192.168.1.100"  // Host IP running Mosquitto Broker
#define MQTT_PORT 1883
#define DEVICE_ID "esp32_001"

// Topics
#define TOPIC_PRESSURE_INLET  "filtration/sensor/pressure/inlet"
#define TOPIC_PRESSURE_OUTLET "filtration/sensor/pressure/outlet"
#define TOPIC_FLOW            "filtration/sensor/flow"
#define TOPIC_CURRENT         "filtration/sensor/current"
#define TOPIC_CONTROL         "filtration/control/#"

// Pin Definitions
#define PIN_PRESSURE_INLET  34
#define PIN_PRESSURE_OUTLET 35
#define PIN_FLOW_SENSOR     23
#define PIN_CURRENT_SENSOR  32
#define PIN_RELAY_BACKWASH  26

#define PUBLISH_INTERVAL_MS 1000

#endif
