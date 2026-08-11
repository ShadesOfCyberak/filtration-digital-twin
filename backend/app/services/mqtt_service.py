import json
import asyncio
import threading
import time
import random
from datetime import datetime
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt

from app.core.config import settings
from app.core.logging import logger
from app.services.data_processing_service import data_processor
from app.services.digital_twin_service import digital_twin_service
from app.services.health_monitoring_service import health_service
from app.services.alert_service import alert_service
from app.repositories.influxdb_repository import influx_repo


class MQTTService:
    def __init__(self):
        self.broker_host = settings.mqtt.broker_host
        self.broker_port = settings.mqtt.broker_port
        self.topic_prefix = settings.mqtt.topic_prefix
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self._simulator_thread = None
        self._running = False
        
        # Latest telemetry frame cache
        self.latest_raw_telemetry: Dict[str, float] = {
            "pressure_inlet": 2.45,
            "pressure_outlet": 1.95,
            "flow": 76.5,
            "current": 3.25
        }

    def start(self):
        self._running = True
        try:
            self.client = mqtt.Client(client_id=settings.mqtt.client_id)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Non-blocking connect
            self.client.connect_async(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            logger.info(f"MQTT Client attempting connection to {self.broker_host}:{self.broker_port}")
        except Exception as e:
            logger.warning(f"MQTT broker connection failed ({e}). Launching background telemetry simulator.")
            self._start_simulator()

    def stop(self):
        self._running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        logger.info("MQTT Service stopped.")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            logger.info("Successfully connected to MQTT Broker!")
            client.subscribe(f"{self.topic_prefix}/sensor/#")
        else:
            logger.warning(f"MQTT connection returned code {rc}. Starting internal telemetry simulator.")
            self._start_simulator()

    def _on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        logger.warning(f"MQTT Client disconnected (rc={rc}).")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic = msg.topic
            
            # Expecting topic format: filtration/sensor/{sensor_type}
            parts = topic.split("/")
            if len(parts) >= 3:
                sensor_id = parts[2]
                val = float(payload.get("value", 0.0))
                self.latest_raw_telemetry[sensor_id] = val
                
                # Ingest through pipeline in background
                asyncio.run(self.process_incoming_data())
        except Exception as e:
            logger.error(f"Error handling MQTT message on {msg.topic}: {e}")

    async def process_incoming_data(self):
        """Run standard telemetry data processing pipeline"""
        # Step 1: Filter & extract features
        processed = data_processor.process_telemetry_frame(self.latest_raw_telemetry)
        
        # Step 2: Update Digital Twin
        twin_state = digital_twin_service.evaluate_twin_state(processed)
        
        # Step 3: Evaluate Health Scores
        health_summary = health_service.evaluate_system_health(processed, twin_state)
        
        # Step 4: Evaluate Alert Rules
        await alert_service.evaluate_rules(processed, twin_state, health_summary)
        
        # Step 5: Persist to database repository
        await influx_repo.write_twin_state(twin_state.dict())
        for sensor_id, val in self.latest_raw_telemetry.items():
            await influx_repo.write_sensor_reading(sensor_id, val)

    def publish_control_command(self, command: str, parameters: dict) -> bool:
        topic = f"{self.topic_prefix}/control/{command}"
        payload = json.dumps({"command": command, "parameters": parameters, "timestamp": datetime.utcnow().isoformat()})
        
        if self.is_connected and self.client:
            self.client.publish(topic, payload, qos=1)
            logger.info(f"Published control command '{command}' to topic {topic}")
            return True
        else:
            logger.info(f"[SIMULATED MQTT] Published command '{command}' with params {parameters}")
            if command == "backwash":
                digital_twin_service.trigger_backwash_reset()
            return True

    def _start_simulator(self):
        if self._simulator_thread and self._simulator_thread.is_alive():
            return
        self._simulator_thread = threading.Thread(target=self._simulator_loop, daemon=True)
        self._simulator_thread.start()
        logger.info("Internal telemetry simulator thread started.")

    def _simulator_loop(self):
        """Simulate continuous sensor readings from physical filtration rig"""
        ci_counter = 0
        while self._running:
            try:
                ci_counter += 1
                # Simulate gradual filter fouling: Pinlet increases slowly, flow drops slightly
                fouling_bias = min(1.2, ci_counter * 0.005)
                
                self.latest_raw_telemetry["pressure_inlet"] = float(np.round(2.4 + fouling_bias + random.uniform(-0.03, 0.03), 3))
                self.latest_raw_telemetry["pressure_outlet"] = float(np.round(1.95 + random.uniform(-0.02, 0.02), 3))
                self.latest_raw_telemetry["flow"] = float(np.round(78.0 - (fouling_bias * 12.0) + random.uniform(-0.5, 0.5), 2))
                self.latest_raw_telemetry["current"] = float(np.round(3.2 + (fouling_bias * 0.8) + random.uniform(-0.05, 0.05), 2))

                # If backwash occurred in twin service, reset fouling bias counter
                if digital_twin_service.time_since_backwash < 2.0:
                    ci_counter = 0

                asyncio.run(self.process_incoming_data())
                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Error in telemetry simulator loop: {e}")
                time.sleep(2.0)


mqtt_service = MQTTService()
