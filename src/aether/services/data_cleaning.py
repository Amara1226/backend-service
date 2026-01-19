from __future__ import annotations

from typing import Any
import pandas as pd


class DataCleaner:
    @staticmethod
    def validate_readings(readings: dict[str, Any], pollutants: list[str]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        if not isinstance(readings, dict) or len(readings) == 0:
            return False, ["readings must be a non-empty object"]

        for k in pollutants:
            if k not in readings:
                errors.append(f"missing '{k}'")
            else:
                v = readings.get(k)
                if not isinstance(v, (int, float)):
                    errors.append(f"'{k}' must be numeric")
        return (len(errors) == 0), errors

    @staticmethod
    def clean_historical(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
        before = len(df)
        df2 = df.copy()

        df2 = df2.dropna(subset=["sensor_id", "timestamp"])

        pollutant_cols = [c for c in df2.columns if c not in ("sensor_id", "timestamp")]
        for c in pollutant_cols:
            df2 = df2[df2[c].notna()]
            df2 = df2[df2[c] >= 0]

        if "pm25" in df2.columns:
            df2 = df2[df2["pm25"] <= 500]

        df2["timestamp"] = pd.to_datetime(df2["timestamp"], errors="coerce")
        df2 = df2.dropna(subset=["timestamp"])

        after = len(df2)
        stats = {
            "rows_loaded": int(before),
            "rows_kept": int(after),
            "rows_dropped": int(before - after),
            "percent_cleaned": float((before - after) / before * 100) if before else 0.0,
        }
        return df2, stats

    @staticmethod
    def categorize_pm25(pm25: pd.Series, thresholds: dict[str, float]) -> pd.Series:
        safe = thresholds["pm25_safe"]
        mod = thresholds["pm25_moderate"]
        dang = thresholds["pm25_danger"]

        cat = pd.Series(["No data"] * len(pm25), index=pm25.index, dtype="object")
        mask = pm25.notna()
        cat.loc[mask & (pm25 <= safe)] = "Safe"
        cat.loc[mask & (pm25 > safe) & (pm25 <= mod)] = "Moderate"
        cat.loc[mask & (pm25 > mod) & (pm25 <= dang)] = "Unhealthy"
        cat.loc[mask & (pm25 > dang)] = "Dangerous"
        return cat
