from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from agents.base_agent import Agent
from core.prompts import TREND_ANALYST_PROMPT


class TrendAnalystAgent(Agent):
    def __init__(self, client=None, deployment_name: str | None = None):
        super().__init__("TrendAnalystAgent", TREND_ANALYST_PROMPT, client, deployment_name)

    def heuristic(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        monthly = df.groupby("month_name", sort=False).agg(
            avg_temp=("tavg", "mean"),
            total_rain=("prcp", "sum"),
            sunshine=("tsun", "sum"),
        )
        hottest_month = monthly["avg_temp"].idxmax()
        coolest_month = monthly["avg_temp"].idxmin()
        wettest_month = monthly["total_rain"].idxmax()
        brightest_month = monthly["sunshine"].idxmax()
        corr = df[["tavg", "prcp", "wspd", "pres", "tsun"]].corr(numeric_only=True)
        temp_sun_corr = float(corr.loc["tavg", "tsun"])
        temp_pres_corr = float(corr.loc["tavg", "pres"])
        return {
            "status": "ok",
            "agent": self.name,
            "summary": "Seasonal structure is clear, with temperature and sunshine moving together more strongly than temperature and pressure.",
            "bullets": [
                f"{hottest_month} is the hottest month on average, while {coolest_month} is the coolest.",
                f"{wettest_month} has the highest total rainfall in the combined data window.",
                f"{brightest_month} has the highest sunshine accumulation.",
            ],
            "risks": [
                "Rainfall can be episodic, so monthly totals may hide short extreme events.",
            ],
            "recommendations": [
                "Use monthly groupings for seasonal communication and daily data for operations.",
                "Pair sunshine and temperature when explaining comfort or outdoor suitability.",
            ],
            "derived_metrics": {
                "temperature_sunshine_correlation": round(temp_sun_corr, 3),
                "temperature_pressure_correlation": round(temp_pres_corr, 3),
            },
        }
