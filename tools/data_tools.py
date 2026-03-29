from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


NUMERIC_COLUMNS = ["tavg", "tmin", "tmax", "prcp", "wspd", "wpgt", "pres", "tsun"]


def get_climate_summary(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {"error": "Dataset is empty."}

    summary: dict[str, Any] = {
        "records": int(len(df)),
        "date_range": {
            "start": df["date"].min().strftime("%Y-%m-%d"),
            "end": df["date"].max().strftime("%Y-%m-%d"),
        },
        "missing_values": {col: int(df[col].isna().sum()) for col in df.columns if col in NUMERIC_COLUMNS},
        "metrics": {},
        "monthly_temperature": [],
        "monthly_rainfall": [],
    }

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            summary["metrics"][col] = {
                "mean": None if df[col].dropna().empty else round(float(df[col].mean()), 2),
                "min": None if df[col].dropna().empty else round(float(df[col].min()), 2),
                "max": None if df[col].dropna().empty else round(float(df[col].max()), 2),
            }

    monthly = (
        df.groupby("year_month", as_index=False)
        .agg(tavg_mean=("tavg", "mean"), prcp_total=("prcp", "sum"), tsun_total=("tsun", "sum"))
        .fillna(0)
    )
    summary["monthly_temperature"] = [
        {"year_month": row["year_month"], "tavg_mean": round(float(row["tavg_mean"]), 2)}
        for _, row in monthly.iterrows()
    ]
    summary["monthly_rainfall"] = [
        {"year_month": row["year_month"], "prcp_total": round(float(row["prcp_total"]), 2)}
        for _, row in monthly.iterrows()
    ]

    return summary


def detect_anomalies(df: pd.DataFrame, z_threshold: float = 2.0) -> dict[str, Any]:
    if df.empty:
        return {"error": "Dataset is empty."}

    anomaly_output: dict[str, Any] = {"threshold": z_threshold, "counts": {}, "events": {}}
    target_columns = ["tavg", "prcp", "wspd"]

    for col in target_columns:
        series = df[col].dropna()
        if series.empty or series.std(ddof=0) == 0:
            anomaly_output["counts"][col] = 0
            anomaly_output["events"][col] = []
            continue

        z_scores = (df[col] - series.mean()) / series.std(ddof=0)
        flagged = df.loc[z_scores.abs() >= z_threshold, ["date", col]].copy()
        flagged["date"] = flagged["date"].dt.strftime("%Y-%m-%d")
        flagged[col] = flagged[col].round(2)
        events = flagged.to_dict(orient="records")

        anomaly_output["counts"][col] = len(events)
        anomaly_output["events"][col] = events[:15]

    return anomaly_output
