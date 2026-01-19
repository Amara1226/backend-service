from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from aether.config import ServerConfig
from aether.domain.sensor import SensorInfo
from aether.services.data_cleaning import DataCleaner


class TemporalVisualizer:
    def __init__(self, config: ServerConfig):
        self._config = config

    def create_time_series_html(self, df: pd.DataFrame, sensor_id: str) -> str:
        fig = go.Figure()
        for pol in self._config.pollutants:
            if pol in df.columns:
                fig.add_trace(go.Scatter(x=df["timestamp"], y=df[pol], mode="lines", name=pol.upper()))
        fig.update_layout(title=f"Historical Readings: {sensor_id}", hovermode="x unified")
        fig.update_xaxes(rangeslider_visible=True)
        return fig.to_html(include_plotlyjs="cdn", full_html=True)

    def create_distribution_html(self, df: pd.DataFrame, sensors: dict[str, SensorInfo], year: int, month: int) -> str:
        if df.empty:
            raise FileNotFoundError("No data")

        province_map = {sid: s.metadata.get("province", "Unknown") for sid, s in sensors.items()}
        df2 = df.copy()
        df2["province"] = df2["sensor_id"].map(province_map).fillna("Unknown")
        df2["category"] = DataCleaner.categorize_pm25(df2["pm25"], self._config.thresholds)

        counts = df2.groupby(["province", "category"]).size().reset_index(name="count")
        totals = counts.groupby("province")["count"].transform("sum")
        counts["percent"] = (counts["count"] / totals) * 100.0

        categories_order = ["Safe", "Moderate", "Unhealthy", "Dangerous", "No data"]
        provinces = sorted(counts["province"].unique().tolist())

        fig = go.Figure()
        for cat in categories_order:
            sub = counts[counts["category"] == cat].set_index("province").reindex(provinces).fillna({"percent": 0.0})
            fig.add_trace(
                go.Bar(
                    name=cat,
                    x=provinces,
                    y=sub["percent"],
                    text=sub["percent"].round(1).astype(str) + "%",
                    textposition="inside",
                )
            )

        fig.update_layout(
            title=f"PM2.5 Distribution by Province ({year}-{month:02d})",
            barmode="stack",
            yaxis=dict(range=[0, 100], title="Percent"),
        )
        return fig.to_html(include_plotlyjs="cdn", full_html=True)
