"""Custom tools exposed to agents via tool-calling and used directly in Python."""

from __future__ import annotations

import json
from typing import Any, Dict, List

import numpy as np
import pandas as pd


def compute_summary_stats(df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "date_start": str(df["date"].min().date()) if "date" in df.columns else None,
        "date_end": str(df["date"].max().date()) if "date" in df.columns else None,
        "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
        "stats": {},
    }
    for col in columns:
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        summary["stats"][col] = {
            "mean": round(float(series.mean()), 3),
            "median": round(float(series.median()), 3),
            "std": round(float(series.std()), 3),
            "min": round(float(series.min()), 3),
            "max": round(float(series.max()), 3),
        }
    return summary


def detect_outliers(df: pd.DataFrame, column: str, z_threshold: float = 2.5) -> Dict[str, Any]:
    if column not in df.columns:
        return {"column": column, "anomalies": [], "count": 0, "status": "missing_column"}
    series = pd.to_numeric(df[column], errors="coerce")
    clean = series.dropna()
    if clean.empty or float(clean.std(ddof=0)) == 0.0:
        return {"column": column, "anomalies": [], "count": 0, "status": "insufficient_variation"}

    z_scores = (series - clean.mean()) / clean.std(ddof=0)
    mask = z_scores.abs() >= z_threshold
    anomaly_rows = df.loc[mask, ["date", column]].copy()
    anomaly_rows["z_score"] = z_scores[mask].round(3)
    anomaly_rows = anomaly_rows.sort_values(by="z_score", key=lambda s: s.abs(), ascending=False)

    return {
        "column": column,
        "threshold": z_threshold,
        "count": int(mask.sum()),
        "anomalies": [
            {
                "date": str(row["date"].date()) if hasattr(row["date"], "date") else str(row["date"]),
                "value": round(float(row[column]), 3),
                "z_score": round(float(row["z_score"]), 3),
            }
            for _, row in anomaly_rows.head(12).iterrows()
        ],
    }


def generate_chart_metadata(metric: str) -> Dict[str, str]:
    presets = {
        "temperature": {
            "title": "Temperature Over Time",
            "x": "date",
            "y": "tavg",
            "hint": "Use a line chart to show daily variability and seasonal movement.",
        },
        "rainfall": {
            "title": "Monthly Rainfall Totals",
            "x": "month",
            "y": "prcp",
            "hint": "Use bars to make accumulated precipitation easy to compare.",
        },
        "sunshine": {
            "title": "Monthly Sunshine Duration",
            "x": "month",
            "y": "tsun",
            "hint": "Highlight bright vs low-light periods across the year.",
        },
    }
    return presets.get(
        metric,
        {
            "title": f"{metric.title()} Chart",
            "x": "date",
            "y": metric,
            "hint": "Choose the simplest chart that communicates the pattern clearly.",
        },
    )


TOOL_REGISTRY = {
    "compute_summary_stats": compute_summary_stats,
    "detect_outliers": detect_outliers,
    "generate_chart_metadata": generate_chart_metadata,
}


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "compute_summary_stats",
            "description": "Compute descriptive statistics and missingness for selected climate columns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Numeric climate columns to summarise.",
                    }
                },
                "required": ["columns"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_outliers",
            "description": "Detect unusually high or low values in a climate column using z-scores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {"type": "string"},
                    "z_threshold": {"type": "number", "default": 2.5},
                },
                "required": ["column"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_chart_metadata",
            "description": "Return chart title and axis recommendations for a climate metric.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string"},
                },
                "required": ["metric"],
            },
        },
    },
]


def execute_tool(tool_name: str, arguments_json: str, df: pd.DataFrame) -> str:
    args = json.loads(arguments_json or "{}")
    if tool_name == "compute_summary_stats":
        result = compute_summary_stats(df, columns=args.get("columns", []))
    elif tool_name == "detect_outliers":
        result = detect_outliers(
            df,
            column=args.get("column", "tavg"),
            z_threshold=float(args.get("z_threshold", 2.5)),
        )
    elif tool_name == "generate_chart_metadata":
        result = generate_chart_metadata(metric=args.get("metric", "temperature"))
    else:
        result = {"status": "error", "message": f"Unknown tool: {tool_name}"}
    return json.dumps(result)
