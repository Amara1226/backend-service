from __future__ import annotations

from typing import Any
import pandas as pd
import plotly.express as px

from aether.config import ServerConfig
from aether.domain.sensor import SensorInfo
from aether.services.data_cleaning import DataCleaner


class MapVisualizer:
    def __init__(self, config: ServerConfig):
        self._config = config

    def create_map_html(self, sensors: dict[str, SensorInfo]) -> str:
        rows: list[dict[str, Any]] = []
        for s in sensors.values():
            pm25 = None
            if s.last_reading and "pm25" in s.last_reading:
                pm25 = s.last_reading.get("pm25")
            rows.append(
                {
                    "sensor_id": s.id,
                    "lat": s.latitude,
                    "lon": s.longitude,
                    "province": s.metadata.get("province", "Unknown"),
                    "region": s.metadata.get("region", "Unknown"),
                    "pm25": pm25,
                }
            )

        df = pd.DataFrame(rows)
        df["category"] = DataCleaner.categorize_pm25(df["pm25"], self._config.thresholds)

        scatter_fn = getattr(px, "scatter_map", None) or getattr(px, "scatter_mapbox")
        fig = scatter_fn(
            df,
            lat="lat",
            lon="lon",
            hover_name="sensor_id",
            hover_data={"province": True, "region": True, "pm25": True, "lat": False, "lon": False},
            color="category",
            zoom=int(self._config.map_config.get("default_zoom", 7)),
        )
        fig.update_layout(mapbox_style=self._config.map_config.get("map_style", "open-street-map"))
        return fig.to_html(include_plotlyjs="cdn", full_html=True)
