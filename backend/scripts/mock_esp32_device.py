#!/usr/bin/env python3
"""
Independent ESP32 IoT Device Simulator
Continuously streams simulated physical sensor data to the backend endpoint every 3 seconds.

Supports:
1. Direct HTTP POST ingestion: http://localhost:8000/api/v1/sensors/telemetry (default)
2. MQTT Broker publishing: Mosquitto on port 1883 (with --protocol mqtt)
"""

import sys
import time
import json
import random
import argparse
from datetime import datetime

# Standard library urllib for zero-dependency HTTP fallback if requests is not installed
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

try:
    import paho.mqtt.client as mqtt
    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False


class MockESP32Device:
    def __init__(
        self,
        endpoint_url: str = "http://localhost:8000/api/v1/sensors/telemetry",
        protocol: str = "http",
        broker_host: str = "localhost",
        broker_port: int = 1883,
        device_id: str = "esp32_001",
        interval: float = 3.0,
        scenario: str = "fouling"
    ):
        self.endpoint_url = endpoint_url
        self.protocol = protocol.lower()
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.device_id = device_id
        self.interval = interval
        self.scenario = scenario
        self.step = 0
        self.mqtt_client = None

        if self.protocol == "mqtt":
            self._init_mqtt()

    def _init_mqtt(self):
        if not HAS_MQTT:
            print("[ERROR] paho-mqtt package is not installed. Please run: pip install paho-mqtt")
            sys.exit(1)
        try:
            self.mqtt_client = mqtt.Client(client_id=f"mock_{self.device_id}")
            self.mqtt_client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.mqtt_client.loop_start()
            print(f"[MQTT] Connected to Mosquitto broker at {self.broker_host}:{self.broker_port}")
        except Exception as e:
            print(f"[WARNING] MQTT connection to {self.broker_host}:{self.broker_port} failed: {e}")
            print("[INFO] Falling back to direct HTTP ingestion endpoint.")
            self.protocol = "http"

    def generate_telemetry_frame(self) -> dict:
        """
        Simulate realistic sensor physics for industrial filtration loop
        """
        self.step += 1

        if self.scenario == "fouling":
            # Realistic progressive filter cake accumulation over time
            fouling = min(1.4, self.step * 0.008)
            p_inlet = round(2.35 + fouling + random.uniform(-0.02, 0.02), 3)
            p_outlet = round(1.92 + random.uniform(-0.015, 0.015), 3)
            flow = round(max(20.0, 78.5 - (fouling * 14.0) + random.uniform(-0.4, 0.4)), 2)
            current = round(3.20 + (fouling * 0.85) + random.uniform(-0.04, 0.04), 2)
        elif self.scenario == "clogged":
            # Severe fouling state
            p_inlet = round(3.85 + random.uniform(-0.03, 0.03), 3)
            p_outlet = round(1.80 + random.uniform(-0.02, 0.02), 3)
            flow = round(34.0 + random.uniform(-0.8, 0.8), 2)
            current = round(4.85 + random.uniform(-0.06, 0.06), 2)
        elif self.scenario == "leak":
            # Pipe rupture or downstream seal failure
            p_inlet = round(1.40 + random.uniform(-0.02, 0.02), 3)
            p_outlet = round(0.40 + random.uniform(-0.02, 0.02), 3)
            flow = round(92.0 + random.uniform(-0.5, 0.5), 2)
            current = round(2.40 + random.uniform(-0.04, 0.04), 2)
        else:
            # Baseline normal nominal operating condition
            p_inlet = round(2.40 + random.uniform(-0.02, 0.02), 3)
            p_outlet = round(1.95 + random.uniform(-0.02, 0.02), 3)
            flow = round(77.0 + random.uniform(-0.5, 0.5), 2)
            current = round(3.25 + random.uniform(-0.04, 0.04), 2)

        return {
            "device_id": self.device_id,
            "pressure_inlet": p_inlet,
            "pressure_outlet": p_outlet,
            "flow": flow,
            "current": current,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def send_http(self, payload: dict) -> bool:
        start_t = time.time()
        json_data = json.dumps(payload).encode("utf-8")

        if HAS_REQUESTS:
            try:
                res = requests.post(
                    self.endpoint_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=5.0
                )
                latency_ms = int((time.time() - start_t) * 1000)
                if res.status_code in (200, 201):
                    resp_json = res.json().get("data", {})
                    dp = round(payload["pressure_inlet"] - payload["pressure_outlet"], 3)
                    ci = resp_json.get("clogging_index", "N/A")
                    health = resp_json.get("system_health", "N/A")
                    sync = resp_json.get("synchronization_state", "N/A")

                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] [#{self.step:04d}] "
                        f"HTTP POST 201 OK ({latency_ms}ms) | "
                        f"Pin: {payload['pressure_inlet']:.2f} bar | "
                        f"Pout: {payload['pressure_outlet']:.2f} bar | "
                        f"ΔP: {dp:.2f} bar | "
                        f"Flow: {payload['flow']:.1f} L/min | "
                        f"Curr: {payload['current']:.2f} A -> "
                        f"[Twin: {sync} | CI: {ci} | Health: {health}%]"
                    )
                    return True
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] HTTP Error {res.status_code}: {res.text}")
                    return False
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Connection failed to {self.endpoint_url} ({e})")
                return False
        else:
            # Fallback using standard urllib
            try:
                req = urllib.request.Request(
                    self.endpoint_url,
                    data=json_data,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=5.0) as response:
                    latency_ms = int((time.time() - start_t) * 1000)
                    resp_data = json.loads(response.read().decode("utf-8")).get("data", {})
                    dp = round(payload["pressure_inlet"] - payload["pressure_outlet"], 3)
                    ci = resp_data.get("clogging_index", "N/A")
                    health = resp_data.get("system_health", "N/A")

                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] [#{self.step:04d}] "
                        f"HTTP POST 201 OK ({latency_ms}ms) | "
                        f"Pin: {payload['pressure_inlet']:.2f} bar | "
                        f"Pout: {payload['pressure_outlet']:.2f} bar | "
                        f"ΔP: {dp:.2f} bar | "
                        f"Flow: {payload['flow']:.1f} L/min | "
                        f"Curr: {payload['current']:.2f} A -> [CI: {ci} | Health: {health}%]"
                    )
                    return True
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] HTTP Request failed: {e}")
                return False

    def send_mqtt(self, payload: dict) -> bool:
        if not self.mqtt_client:
            return False

        topics = {
            "filtration/sensor/pressure_inlet": {"value": payload["pressure_inlet"], "unit": "bar"},
            "filtration/sensor/pressure_outlet": {"value": payload["pressure_outlet"], "unit": "bar"},
            "filtration/sensor/flow": {"value": payload["flow"], "unit": "L/min"},
            "filtration/sensor/current": {"value": payload["current"], "unit": "A"}
        }

        for topic, metric in topics.items():
            packet = {
                "device_id": self.device_id,
                "sensor_id": topic.split("/")[-1],
                "value": metric["value"],
                "unit": metric["unit"],
                "quality": "good",
                "timestamp": payload["timestamp"]
            }
            self.mqtt_client.publish(topic, json.dumps(packet), qos=1)

        dp = round(payload["pressure_inlet"] - payload["pressure_outlet"], 3)
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] [#{self.step:04d}] "
            f"MQTT PUBLISH 4 Topics -> "
            f"Pin: {payload['pressure_inlet']:.2f} bar | "
            f"Pout: {payload['pressure_outlet']:.2f} bar | "
            f"ΔP: {dp:.2f} bar | "
            f"Flow: {payload['flow']:.1f} L/min | "
            f"Curr: {payload['current']:.2f} A"
        )
        return True

    def run(self, count: int = 0):
        print("=" * 78)
        print(f"  ESP32 Mock Sensor Node Starting (Device: {self.device_id})")
        print(f"  Protocol: {self.protocol.upper()} | Target: {self.endpoint_url if self.protocol == 'http' else f'{self.broker_host}:{self.broker_port}'}")
        print(f"  Streaming Frequency: every {self.interval:.1f} seconds | Scenario: {self.scenario}")
        print("=" * 78)

        try:
            while True:
                payload = self.generate_telemetry_frame()

                if self.protocol == "mqtt":
                    self.send_mqtt(payload)
                else:
                    self.send_http(payload)

                if count > 0 and self.step >= count:
                    print(f"\n[DONE] Completed {count} iterations.")
                    break

                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n[STOP] User stopped telemetry transmission.")
        finally:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Continuously stream dynamic mock ESP32 telemetry to the backend endpoint"
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        default="http://localhost:8000/api/v1/sensors/telemetry",
        help="Backend HTTP telemetry ingestion endpoint URL"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=3.0,
        help="Interval between transmissions in seconds (default: 3.0)"
    )
    parser.add_argument(
        "--protocol",
        type=str,
        choices=["http", "mqtt"],
        default="http",
        help="Communication protocol: http or mqtt (default: http)"
    )
    parser.add_argument(
        "--broker",
        type=str,
        default="localhost",
        help="MQTT broker host if protocol is mqtt (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=1883,
        help="MQTT broker port if protocol is mqtt (default: 1883)"
    )
    parser.add_argument(
        "--device-id",
        type=str,
        default="esp32_001",
        help="IoT device hardware ID (default: esp32_001)"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        choices=["fouling", "normal", "clogged", "leak"],
        default="fouling",
        help="Simulation scenario: fouling, normal, clogged, leak (default: fouling)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Number of iterations to send (0 = run forever)"
    )

    args = parser.parse_args()

    device = MockESP32Device(
        endpoint_url=args.endpoint,
        protocol=args.protocol,
        broker_host=args.broker,
        broker_port=args.port,
        device_id=args.device_id,
        interval=args.interval,
        scenario=args.scenario
    )
    device.run(count=args.count)
