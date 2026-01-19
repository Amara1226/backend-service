\
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from aether.domain.sensor import SensorInfo

log = logging.getLogger(__name__)

WKT_POINT_PATTERN = re.compile(
    r"POINT\s*\(\s*(?P<lon>-?\d+\.?\d*)\s+(?P<lat>-?\d+\.?\d*)\s*\)",
    re.IGNORECASE,
)


def load_sensors(path: str | Path) -> dict[str, SensorInfo]:
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))
    sensors: dict[str, SensorInfo] = {}

    for entry in raw:
        sid = entry.get("id")
        wkt = entry.get("location", "")
        m = WKT_POINT_PATTERN.search(wkt or "")
        if not sid or not m:
            log.warning("Discarding sensor with invalid id/WKT: %s", entry)
            continue

        lon = float(m.group("lon"))
        lat = float(m.group("lat"))

        if not (-180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0):
            log.warning("Discarding sensor with out-of-range coords: %s (%s, %s)", sid, lon, lat)
            continue

        sensors[sid] = SensorInfo(
            id=sid,
            location=wkt,
            latitude=lat,
            longitude=lon,
            metadata=dict(entry.get("metadata", {})),
        )

    log.info("Loaded sensors: %d (from %d entries)", len(sensors), len(raw))
    return sensors
