from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import pandas as pd


class JsonReadingStorage:
    def __init__(self, storage_path: str | Path):
        self.path = Path(storage_path)

    def load_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def append(self, item: dict[str, Any]) -> None:
        data = self.load_all()
        data.append(item)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class HistoricalCsvRepository:
    def __init__(self, csv_path: str | Path):
        self.path = Path(csv_path)

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.path)
