from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from aether.dependencies import (
    get_sensor_manager,
    get_map_visualizer,
    get_temporal_visualizer,
    initialize_services,
)
from aether.dto.models import IngestRequest, IngestResponse, StatusResponse
from aether.services.exceptions import UnauthorizedSensorError, InvalidReadingError

log = logging.getLogger(__name__)


def create_app(server_config_path: str | None = None, sensors_path: str | None = None) -> FastAPI:
    cfg = server_config_path or os.getenv("AETHER_CONFIG", "config/server_config.json")
    sensors_cfg = sensors_path or os.getenv("AETHER_SENSORS", "config/sensors.json")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logging.basicConfig(level=logging.INFO)
        initialize_services(cfg, sensors_cfg)
        yield

    app = FastAPI(title="Aether AQMS", lifespan=lifespan)

    @app.get("/", response_class=HTMLResponse)
    def welcome() -> str:
        return """<html>
  <head><title>Aether AQMS</title></head>
  <body>
    <h1>Aether AQMS</h1>
    <ul>
      <li><a href="/docs">API Docs</a></li>
      <li><a href="/status">System Status</a></li>
      <li><a href="/map">Real-time Map</a></li>
      <li><code>GET /history/{sensor_id}</code></li>
      <li><code>GET /distribution/{year}/{month}</code></li>
      <li><code>POST /ingest</code></li>
    </ul>
  </body>
</html>
"""

    @app.post("/ingest", response_model=IngestResponse)
    def ingest(req: IngestRequest, sm=Depends(get_sensor_manager)):
        try:
            reading = sm.ingest(req.sensor_id, req.readings, req.timestamp)
            return IngestResponse(status="ok", message="ingested", sensor_id=reading.sensor_id, timestamp=reading.timestamp)
        except UnauthorizedSensorError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except InvalidReadingError as e:
            raise HTTPException(status_code=400, detail={"errors": e.errors})

    @app.get("/map", response_class=HTMLResponse)
    def map_view(sm=Depends(get_sensor_manager), viz=Depends(get_map_visualizer)):
        return viz.create_map_html(sm.sensors)

    @app.get("/status", response_model=StatusResponse)
    def status(sm=Depends(get_sensor_manager)):
        return StatusResponse(**sm.get_status())

    @app.get("/history/{sensor_id}", response_class=HTMLResponse)
    def history(sensor_id: str, sm=Depends(get_sensor_manager), tv=Depends(get_temporal_visualizer)):
        try:
            df = sm.get_sensor_history(sensor_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="sensor not found")
        if df.empty:
            raise HTTPException(status_code=404, detail="no historical data for sensor")
        return tv.create_time_series_html(df, sensor_id)

    @app.get("/distribution/{year}/{month}", response_class=HTMLResponse)
    def distribution(year: int, month: int, sm=Depends(get_sensor_manager), tv=Depends(get_temporal_visualizer)):
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="month must be 1..12")
        df = sm.get_month_df(year, month)
        if df.empty:
            raise HTTPException(status_code=404, detail="no data for the specified period")
        return tv.create_distribution_html(df, sm.sensors, year, month)

    return app


app = create_app()
