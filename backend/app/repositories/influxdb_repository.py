import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point

from app.core.config import settings
from app.core.logging import logger
from app.repositories.base import BaseRepository


class InfluxDBRepository(BaseRepository):
    def __init__(self):
        self.url = settings.db.url
        self.token = settings.db.token
        self.org = settings.db.org
        self.bucket = settings.db.bucket
        self.client: Optional[InfluxDBClientAsync] = None
        self._connected = False
        
        # In-memory buffer fallback for development when InfluxDB is unreachable
        self._memory_sensor_store: List[Dict[str, Any]] = []
        self._memory_twin_store: List[Dict[str, Any]] = []
        self._memory_alert_store: List[Dict[str, Any]] = []
        self._memory_maintenance_store: List[Dict[str, Any]] = []

    async def connect(self) -> bool:
        try:
            self.client = InfluxDBClientAsync(
                url=self.url,
                token=self.token,
                org=self.org
            )
            # Test connectivity
            health = await self.client.health()
            if health.status == "pass":
                self._connected = True
                logger.info(f"Successfully connected to InfluxDB at {self.url}")
                return True
            else:
                logger.warning(f"InfluxDB health check returned: {health.status}. Operating with in-memory fallback.")
                self._connected = False
                return False
        except Exception as e:
            logger.warning(f"Unable to connect to InfluxDB ({e}). Operating in memory fallback mode.")
            self._connected = False
            return False

    async def close(self):
        if self.client and self._connected:
            await self.client.close()
            self._connected = False

    async def write_sensor_reading(self, sensor_id: str, value: float, unit: str = "bar", timestamp: Optional[datetime] = None) -> bool:
        ts = timestamp or datetime.utcnow()
        record = {
            "measurement": "sensor_data",
            "sensor_id": sensor_id,
            "value": value,
            "unit": unit,
            "timestamp": ts.isoformat()
        }
        self._memory_sensor_store.append(record)
        # Keep window of 1000 items in memory
        if len(self._memory_sensor_store) > 1000:
            self._memory_sensor_store.pop(0)

        if not self._connected or not self.client:
            return True

        try:
            point = Point("sensor_data") \
                .tag("sensor_id", sensor_id) \
                .field("value", float(value)) \
                .field("unit", unit) \
                .time(ts)
            write_api = self.client.write_api()
            await write_api.write(bucket=self.bucket, org=self.org, record=point)
            return True
        except Exception as e:
            logger.error(f"Failed to write sensor point to InfluxDB: {e}")
            return False

    async def write_twin_state(self, twin_state: Dict[str, Any]) -> bool:
        ts = twin_state.get("timestamp") or datetime.utcnow()
        self._memory_twin_store.append(twin_state)
        if len(self._memory_twin_store) > 500:
            self._memory_twin_store.pop(0)

        if not self._connected or not self.client:
            return True

        try:
            point = Point("digital_twin_state") \
                .tag("twin_id", twin_state.get("twin_id", "filtration_system_001")) \
                .tag("synchronization_state", twin_state.get("synchronization_state", "SYNCHRONIZED")) \
                .field("actual_pressure_drop", float(twin_state.get("actual_pressure_drop", 0))) \
                .field("expected_pressure_drop", float(twin_state.get("expected_pressure_drop", 0))) \
                .field("pressure_residual", float(twin_state.get("pressure_residual", 0))) \
                .field("actual_flow_rate", float(twin_state.get("actual_flow_rate", 0))) \
                .field("expected_flow_rate", float(twin_state.get("expected_flow_rate", 0))) \
                .field("flow_residual", float(twin_state.get("flow_residual", 0))) \
                .time(ts)
            write_api = self.client.write_api()
            await write_api.write(bucket=self.bucket, org=self.org, record=point)
            return True
        except Exception as e:
            logger.error(f"Failed to write twin state to InfluxDB: {e}")
            return False

    async def write_alert(self, alert_data: Dict[str, Any]) -> bool:
        self._memory_alert_store.append(alert_data)
        if len(self._memory_alert_store) > 200:
            self._memory_alert_store.pop(0)
        return True

    async def get_latest_sensor_data(self) -> Dict[str, Any]:
        latest: Dict[str, Any] = {}
        for item in reversed(self._memory_sensor_store):
            sensor_id = item["sensor_id"]
            if sensor_id not in latest:
                latest[sensor_id] = item
            if len(latest) >= 4:
                break
        return latest

    async def get_sensor_history(self, sensor_id: str, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        history = [
            item for item in self._memory_sensor_store
            if item["sensor_id"] == sensor_id
        ]
        return history[-100:]

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        return self._memory_alert_store[-20:]


    async def write_maintenance_log(self, log_data: Dict[str, Any]) -> bool:
        self._memory_maintenance_store.append(log_data)
        if len(self._memory_maintenance_store) > 100:
            self._memory_maintenance_store.pop(0)
        return True

    async def get_maintenance_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._memory_maintenance_store[-limit:]

    async def get_recent_twin_states(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._memory_twin_store[-limit:]


# Repository Singleton
influx_repo = InfluxDBRepository()
