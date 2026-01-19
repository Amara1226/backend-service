from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from aether.config import ServerConfig
from aether.persistence.storage import JsonReadingStorage, HistoricalCsvRepository
from aether.services.sensor_loader import load_sensors
from aether.services.data_cleaning import DataCleaner
from aether.services.sensor_manager import SensorManager
from aether.visualization.map_visualization import MapVisualizer
from aether.visualization.temporal_visualization import TemporalVisualizer

log = logging.getLogger(__name__)

_sensor_manager: SensorManager | None = None
_map_viz: MapVisualizer | None = None
_temp_viz: TemporalVisualizer | None = None


def initialize_services(server_config_path: str, sensors_path: str) -> None:
    global _sensor_manager, _map_viz, _temp_viz

    config = ServerConfig.load(server_config_path)
    sensors = load_sensors(sensors_path)

    storage_path = Path(config.storage_file)
    hist_path = Path(config.historical_data_file)
    if not storage_path.is_absolute():
        storage_path = Path.cwd() / config.storage_file
    if not hist_path.is_absolute():
        hist_path = Path.cwd() / config.historical_data_file

    storage = JsonReadingStorage(storage_path)
    hist_repo = HistoricalCsvRepository(hist_path)
    raw_df = hist_repo.load()
    cleaned_df, stats = DataCleaner.clean_historical(raw_df)

    started_at = datetime.now(timezone.utc).replace(tzinfo=None)
    _sensor_manager = SensorManager(config, sensors, storage, cleaned_df, stats, started_at)
    _map_viz = MapVisualizer(config)
    _temp_viz = TemporalVisualizer(config)

    log.info("Historical data stats: %s", stats)


def reset_services() -> None:
    global _sensor_manager, _map_viz, _temp_viz
    _sensor_manager = None
    _map_viz = None
    _temp_viz = None


def get_sensor_manager() -> SensorManager:
    if _sensor_manager is None:
        raise RuntimeError("Services not initialized")
    return _sensor_manager


def get_map_visualizer() -> MapVisualizer:
    if _map_viz is None:
        raise RuntimeError("Services not initialized")
    return _map_viz


def get_temporal_visualizer() -> TemporalVisualizer:
    if _temp_viz is None:
        raise RuntimeError("Services not initialized")
    return _temp_viz
