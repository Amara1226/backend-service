from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SensorReading:
    sensor_id: str
    readings: dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "readings": self.readings,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SensorInfo:
    id: str
    location: str
    latitude: float
    longitude: float
    metadata: dict[str, Any]
    last_reading: dict[str, Any] | None = None
    last_update: datetime | None = None
