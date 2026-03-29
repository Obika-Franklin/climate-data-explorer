from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from agents.base_agent import Agent
from core.prompts import DATA_LOADER_PROMPT
from core.tools import compute_summary_stats


class DataLoaderAgent(Agent):
    def __init__(self, client=None, deployment_name: str | None = None):
        super().__init__("DataLoaderAgent", DATA_LOADER_PROMPT, client, deployment_name)

    def heuristic(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        numeric_cols = [c for c in ["tavg", "tmin", "tmax", "prcp", "wspd", "wpgt", "pres", "tsun", "temp_range"] if c in df.columns]
        summary = compute_summary_stats(df, numeric_cols)
        return {
            "status": "ok",
            "agent": self.name,
            "summary": (
                f"Dataset cleaned and validated with {len(df):,} records spanning "
                f"{summary['date_start']} to {summary['date_end']}."
            ),
            "bullets": [
                f"{len(df.columns)} usable columns after dropping near-empty fields.",
                f"Rainfall missing values were filled with 0 where needed.",
                f"Engineered features include temp_range, rolling averages, and event flags.",
            ],
            "risks": [
                "Some original columns were nearly empty and excluded from downstream analysis.",
            ],
            "recommendations": [
                "Preserve daily granularity for anomaly analysis.",
                "Use the cleaned combined dataset for deployment and grading.",
            ],
            "tool_summary": summary,
        }
