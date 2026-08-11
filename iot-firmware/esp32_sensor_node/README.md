# ESP32 IoT Sensor Node Firmware

This directory contains the C++/Arduino firmware for the ESP32 microcontroller reading physical sensors on the liquid filtration rig.

## Required Libraries:
- `WiFi.h` (Built-in ESP32 core)
- `PubSubClient` (Nick O'Leary MQTT Library)
- `ArduinoJson` (v6.x by Benoit Blanchon)

## Flashing Instructions:
1. Open `esp32_sensor_node.ino` in Arduino IDE or VS Code PlatformIO.
2. Update `config.h` with your WiFi SSID, password, and Mosquitto broker IP address.
3. Select `ESP32 Dev Module` board and correct COM port.
4. Upload firmware.
