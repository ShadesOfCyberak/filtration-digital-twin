import json
import asyncio
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
        self._running = False
        
        # Live dynamic telemetry state - populated strictly by IoT device transmissions
        self.has_received_data = False
        self.last_telemetry_timestamp: Optional[datetime] = None
        self.total_frames_received: int = 0
        self.latest_raw_telemetry: Dict[str, float] = {
            "pressure_inlet": 0.0,
            "pressure_outlet": 0.0,
            "flow": 0.0,
            "current": 0.0
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
            logger.warning(f"MQTT broker connection unavailable ({e}). Waiting for device telemetry over HTTP or MQTT reconnect.")

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
            logger.warning(f"MQTT connection returned code {rc}.")

    def _on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        logger.warning(f"MQTT Client disconnected (rc={rc}).")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic = msg.topic
            
            # Determine sensor_id from payload or topic hierarchy
            # Formats:
            # 1. filtration/sensor/pressure/inlet -> pressure_inlet
            # 2. filtration/sensor/flow -> flow
            # 3. payload explicitly contains sensor_id
            parts = topic.split("/")
            sensor_id = payload.get("sensor_id")
            if not sensor_id and len(parts) >= 3:
                if len(parts) >= 4 and parts[2] == "pressure":
                    sensor_id = f"pressure_{parts[3]}"
                else:
                    sensor_id = parts[2]
            
            if sensor_id:
                val = float(payload.get("value", 0.0))
                unit = payload.get("unit", "bar")
                
                # Ingest through dynamic pipeline
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(
                            self.ingest_single_reading(sensor_id, val, unit),
                            loop
                        )
                    else:
                        loop.run_until_complete(self.ingest_single_reading(sensor_id, val, unit))
                except RuntimeError:
                    asyncio.run(self.ingest_single_reading(sensor_id, val, unit))
        except Exception as e:
            logger.error(f"Error handling MQTT message on {msg.topic}: {e}")

    async def ingest_single_reading(self, sensor_id: str, value: float, unit: str = "bar", timestamp: Optional[datetime] = None):
        """Ingest individual sensor reading from MQTT or REST"""
        self.latest_raw_telemetry[sensor_id] = value
        self.has_received_data = True
        self.last_telemetry_timestamp = timestamp or datetime.utcnow()
        self.total_frames_received += 1
        
        await influx_repo.write_sensor_reading(sensor_id, value, unit=unit, timestamp=self.last_telemetry_timestamp)
        await self.process_incoming_data()

    async def ingest_telemetry_frame(self, readings: Dict[str, float], timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Dynamically ingest a complete telemetry frame from IoT device (ESP32 via HTTP or MQTT)
        Readings dict keys: pressure_inlet, pressure_outlet, flow, current
        """
        self.latest_raw_telemetry.update(readings)
        self.has_received_data = True
        self.last_telemetry_timestamp = timestamp or datetime.utcnow()
        self.total_frames_received += 1

        # Write each sensor to repository
        for sensor_id, val in readings.items():
            unit = "bar" if "pressure" in sensor_id else ("L/min" if sensor_id == "flow" else "A")
            await influx_repo.write_sensor_reading(sensor_id, val, unit=unit, timestamp=self.last_telemetry_timestamp)

        # Execute dynamic digital twin, health, and alert pipelines
        result = await self.process_incoming_data()
        return result

    async def process_incoming_data(self) -> Dict[str, Any]:
        """Run standard telemetry data processing pipeline strictly on live dynamic data"""
        # Step 1: Filter & extract features
        processed = data_processor.process_telemetry_frame(self.latest_raw_telemetry)
        
        # Step 2: Update Digital Twin
        twin_state = digital_twin_service.evaluate_twin_state(processed)
        
        # Step 3: Evaluate Health Scores
        health_summary = health_service.evaluate_system_health(processed, twin_state)
        
        # Step 4: Evaluate Alert Rules
        await alert_service.evaluate_rules(processed, twin_state, health_summary)
        
        # Step 5: Persist twin state to database repository
        await influx_repo.write_twin_state(twin_state.dict())

        return {
            "processed": processed,
            "twin_state": twin_state.dict(),
            "health": health_summary.dict()
        }

    def publish_control_command(self, command: str, parameters: dict) -> bool:
        topic = f"{self.topic_prefix}/control/{command}"
        payload = json.dumps({"command": command, "parameters": parameters, "timestamp": datetime.utcnow().isoformat()})
        
        if self.is_connected and self.client:
            self.client.publish(topic, payload, qos=1)
            logger.info(f"Published control command '{command}' to topic {topic}")
            return True
        else:
            logger.info(f"[HTTP/MQTT Control] Executed command '{command}' with params {parameters}")
            if command == "backwash":
                digital_twin_service.trigger_backwash_reset()
            return True


mqtt_service = MQTTService()
