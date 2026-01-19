from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from aether.config import ServerConfig
from aether.domain.sensor import SensorReading, SensorInfo
from aether.persistence.storage import JsonReadingStorage
from aether.services.data_cleaning import DataCleaner
from aether.services.exceptions import UnauthorizedSensorError, InvalidReadingError


@dataclass
class SensorManagerState:
    total_readings: int = 0
    last_update: datetime | None = None


class SensorManager:
    def __init__(
        self,
        config: ServerConfig,
        sensors: dict[str, SensorInfo],
        storage: JsonReadingStorage,
        historical_df: pd.DataFrame,
        historical_stats: dict[str, Any],
        started_at: datetime,
    ):
        self._config = config
        self._sensors = sensors
        self._storage = storage
        self._historical_df = historical_df
        self._historical_stats = historical_stats
        self._started_at = started_at
        self._state = SensorManagerState()
        self._hydrate_from_storage()

    @property
    def config(self) -> ServerConfig:
        return self._config

    @property
    def sensors(self) -> dict[str, SensorInfo]:
        return self._sensors

    @property
    def historical_df(self) -> pd.DataFrame:
        return self._historical_df

    def _hydrate_from_storage(self) -> None:
        data = self._storage.load_all()
        self._state.total_readings = len(data)

        last = None
        for item in data:
            sid = item.get("sensor_id")
            ts = item.get("timestamp")
            if sid in self._sensors and ts:
                try:
                    dttm = datetime.fromisoformat(ts)
                except ValueError:
                    continue
                self._sensors[sid].last_reading = item.get("readings")
                self._sensors[sid].last_update = dttm
                last = dttm if last is None or dttm > last else last
        self._state.last_update = last

    def ingest(self, sensor_id: str, readings: dict[str, Any], timestamp: datetime | None) -> SensorReading:
        if sensor_id not in self._sensors:
            raise UnauthorizedSensorError(f"sensor '{sensor_id}' is not authorized")

        ok, errors = DataCleaner.validate_readings(readings, self._config.pollutants)
        if not ok:
            raise InvalidReadingError(errors)

        ts = timestamp or datetime.now(timezone.utc).replace(tzinfo=None)
        reading = SensorReading(sensor_id=sensor_id, readings=readings, timestamp=ts)

        self._storage.append(reading.to_dict())
        self._state.total_readings += 1
        self._state.last_update = ts

        info = self._sensors[sensor_id]
        info.last_reading = readings
        info.last_update = ts
        return reading

    def get_status(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        uptime = int((now - self._started_at).total_seconds())
        active = sum(1 for s in self._sensors.values() if s.last_update is not None)
        return {
            "status": "healthy" if active > 0 else "degraded",
            "uptime_seconds": uptime,
            "active_sensors": active,
            "total_readings": self._state.total_readings,
            "last_update": self._state.last_update,
        }

    def get_sensor_history(self, sensor_id: str) -> pd.DataFrame:
        if sensor_id not in self._sensors:
            raise KeyError(sensor_id)
        return self._historical_df[self._historical_df["sensor_id"] == sensor_id].sort_values("timestamp")

    def get_month_df(self, year: int, month: int) -> pd.DataFrame:
        df = self._historical_df.copy()
        df["year"] = df["timestamp"].dt.year
        df["month"] = df["timestamp"].dt.month
        return df[(df["year"] == year) & (df["month"] == month)]
