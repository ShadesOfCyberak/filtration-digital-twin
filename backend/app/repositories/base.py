from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseRepository(ABC):
    @abstractmethod
    async def write_sensor_reading(self, sensor_id: str, value: float, unit: str = "bar", timestamp: Optional[datetime] = None) -> bool:
        pass

    @abstractmethod
    async def get_latest_sensor_data(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_sensor_history(self, sensor_id: str, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        pass
