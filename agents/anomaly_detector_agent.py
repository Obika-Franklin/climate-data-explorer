from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from agents.base_agent import Agent
from core.prompts import ANOMALY_DETECTOR_PROMPT
from core.tools import detect_outliers


class AnomalyDetectorAgent(Agent):
    def __init__(self, client=None, deployment_name: str | None = None):
        super().__init__("AnomalyDetectorAgent", ANOMALY_DETECTOR_PROMPT, client, deployment_name)

    def heuristic(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        metrics = ["tavg", "prcp", "wspd", "pres"]
        results = {metric: detect_outliers(df, metric, z_threshold=2.5) for metric in metrics}
        top_events = []
        for metric, payload in results.items():
            for item in payload.get("anomalies", [])[:3]:
                top_events.append({"metric": metric, **item})
        top_events = sorted(top_events, key=lambda x: abs(x.get("z_score", 0)), reverse=True)[:8]
        return {
            "status": "ok",
            "agent": self.name,
            "summary": "The data contains a manageable set of extreme events concentrated in rainfall, wind, temperature, and pressure tails.",
            "bullets": [
                f"Detected {results['tavg']['count']} temperature anomalies.",
                f"Detected {results['prcp']['count']} rainfall anomalies.",
                f"Detected {results['wspd']['count']} wind-speed anomalies.",
                f"Detected {results['pres']['count']} pressure anomalies.",
            ],
            "risks": [
                "Single-day outliers can disproportionately shape user perception unless contextualised.",
            ],
            "recommendations": [
                "Show anomalies on top of the daily time series for interpretability.",
                "Keep anomaly sensitivity user-adjustable in the UI.",
            ],
            "top_events": top_events,
            "full_results": results,
        }
