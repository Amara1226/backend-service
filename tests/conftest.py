import json
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from aether.dependencies import reset_services


@pytest.fixture()
def client(tmp_path: Path):
    cfg_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    cfg_dir.mkdir()
    data_dir.mkdir()

    (data_dir / "readings.json").write_text("[]", encoding="utf-8")

    sensors = [
        {"id": "sensor_ok_001", "location": "POINT(4.9041 52.3676)", "metadata": {"province": "North Holland"}},
        {"id": "sensor_bad_001", "location": "POINT(2000 9999)", "metadata": {}},
    ]
    (cfg_dir / "sensors.json").write_text(json.dumps(sensors, indent=2), encoding="utf-8")

    df = pd.DataFrame(
        [
            {"sensor_id": "sensor_ok_001", "timestamp": "2024-01-01T00:00:00", "pm25": 10, "pm10": 20, "no2": 5, "o3": 30},
            {"sensor_id": "sensor_ok_001", "timestamp": "2024-01-01T01:00:00", "pm25": 80, "pm10": 120, "no2": 6, "o3": 31},
            {"sensor_id": "sensor_ok_001", "timestamp": "2024-01-01T02:00:00", "pm25": -1, "pm10": 10, "no2": 1, "o3": 10},
        ]
    )
    df.to_csv(data_dir / "historical.csv", index=False)

    server_config = {
        "storage_file": str(data_dir / "readings.json"),
        "historical_data_file": str(data_dir / "historical.csv"),
        "host": "127.0.0.1",
        "port": 8000,
        "pollutants": ["pm25", "pm10", "no2", "o3"],
        "thresholds": {
            "pm25_safe": 25.0,
            "pm25_moderate": 50.0,
            "pm25_danger": 75.0,
            "pm10_safe": 50.0,
            "pm10_moderate": 100.0,
            "pm10_danger": 150.0
        },
        "map_config": {"default_zoom": 7, "map_style": "open-street-map"},
        "category_colors": {"No data": "gray", "Safe": "green", "Moderate": "yellow", "Unhealthy": "orange", "Dangerous": "red"},
    }
    (cfg_dir / "server_config.json").write_text(json.dumps(server_config, indent=2), encoding="utf-8")

    reset_services()
    from aether.main import create_app

    app = create_app(str(cfg_dir / "server_config.json"), str(cfg_dir / "sensors.json"))
    with TestClient(app) as c:
        yield c
    reset_services()
