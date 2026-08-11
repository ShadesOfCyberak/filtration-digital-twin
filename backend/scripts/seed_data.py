import json
import time
import random
import argparse
from datetime import datetime
import paho.mqtt.client as mqtt


def run_simulator(broker_host: str, broker_port: int, interval: float, duration: int):
    client = mqtt.Client(client_id="telemetry_seed_script")
    try:
        client.connect(broker_host, broker_port, keepalive=60)
        client.loop_start()
        print(f"Connected to MQTT broker at {broker_host}:{broker_port}. Streaming simulated telemetry...")
    except Exception as e:
        print(f"Failed to connect to MQTT broker ({e}). Exiting.")
        return

    start_time = time.time()
    step = 0
    try:
        while True:
            if duration > 0 and (time.time() - start_time) > duration:
                break
            step += 1
            # Simulate progressive filter fouling curve
            fouling = min(1.5, step * 0.01)
            
            p_inlet = 2.45 + fouling + random.uniform(-0.02, 0.02)
            p_outlet = 1.95 + random.uniform(-0.02, 0.02)
            flow = max(15.0, 78.0 - (fouling * 15.0) + random.uniform(-0.4, 0.4))
            current = 3.2 + (fouling * 0.9) + random.uniform(-0.05, 0.05)

            payloads = {
                "filtration/sensor/pressure/inlet": {"value": round(p_inlet, 3), "unit": "bar", "device_id": "esp32_001"},
                "filtration/sensor/pressure/outlet": {"value": round(p_outlet, 3), "unit": "bar", "device_id": "esp32_001"},
                "filtration/sensor/flow": {"value": round(flow, 2), "unit": "L/min", "device_id": "esp32_001"},
                "filtration/sensor/current": {"value": round(current, 2), "unit": "A", "device_id": "esp32_001"}
            }

            for topic, data in payloads.items():
                data["timestamp"] = datetime.utcnow().isoformat() + "Z"
                client.publish(topic, json.dumps(data), qos=1)

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Step {step} | Inlet: {p_inlet:.2f}bar | Outlet: {p_outlet:.2f}bar | Flow: {flow:.1f}L/min | Current: {current:.2f}A")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopping telemetry simulator.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate ESP32 IoT telemetry output")
    parser.add_argument("--host", type=str, default="localhost", help="MQTT Broker Host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT Broker Port")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval in seconds")
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds (0 for infinite)")
    args = parser.parse_args()

    run_simulator(args.host, args.port, args.interval, args.duration)
