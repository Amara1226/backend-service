from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    sensor_id: str = Field(..., min_length=1)
    readings: dict[str, float] = Field(default_factory=dict)
    timestamp: datetime | None = None


class IngestResponse(BaseModel):
    status: str
    message: str
    sensor_id: str
    timestamp: datetime


class StatusResponse(BaseModel):
    status: str
    uptime_seconds: int
    active_sensors: int
    total_readings: int
    last_update: datetime | None
