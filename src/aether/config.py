from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any


@dataclass(frozen=True)
class ServerConfig:
    storage_file: str
    historical_data_file: str
    host: str
    port: int
    pollutants: list[str]
    thresholds: dict[str, float]
    map_config: dict[str, Any]
    category_colors: dict[str, str]

    @staticmethod
    def load(path: str | Path) -> "ServerConfig":
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))
        return ServerConfig(
            storage_file=data["storage_file"],
            historical_data_file=data["historical_data_file"],
            host=data["host"],
            port=int(data["port"]),
            pollutants=list(data.get("pollutants", ["pm25", "pm10", "no2", "o3"])),
            thresholds=dict(data["thresholds"]),
            map_config=dict(data.get("map_config", {})),
            category_colors=dict(data.get("category_colors", {})),
        )
