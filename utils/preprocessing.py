"""Preprocessing helpers for the climate explorer."""

from __future__ import annotations

from typing import List, Tuple

import pandas as pd

REQUIRED_COLUMNS = ["date", "tavg", "tmin", "tmax", "prcp", "wspd", "wpgt", "pres", "tsun"]
OPTIONAL_DROP_COLUMNS = ["snow", "wdir"]


def validate_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing) == 0, missing


def clean_climate_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned = cleaned.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])

    for col in OPTIONAL_DROP_COLUMNS:
        if col in cleaned.columns and cleaned[col].isna().mean() > 0.95:
            cleaned = cleaned.drop(columns=[col])

    numeric_cols = [col for col in cleaned.columns if col != "date"]
    for col in numeric_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    if "prcp" in cleaned.columns:
        cleaned["prcp"] = cleaned["prcp"].fillna(0)

    cleaned = cleaned.reset_index(drop=True)
    return add_features(cleaned)


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["year"] = enriched["date"].dt.year
    enriched["month"] = enriched["date"].dt.month
    enriched["month_name"] = enriched["date"].dt.strftime("%b")
    enriched["quarter"] = enriched["date"].dt.quarter
    enriched["temp_range"] = enriched["tmax"] - enriched["tmin"]
    enriched["rain_flag"] = (enriched["prcp"].fillna(0) > 0).astype(int)
    enriched["high_wind_flag"] = (enriched["wspd"] >= enriched["wspd"].quantile(0.9)).astype(int)
    enriched["tavg_7d"] = enriched["tavg"].rolling(7, min_periods=1).mean()
    enriched["prcp_7d"] = enriched["prcp"].rolling(7, min_periods=1).sum()
    return enriched


def combine_csv_files(file_paths: List[str]) -> pd.DataFrame:
    frames = [pd.read_csv(path) for path in file_paths]
    combined = pd.concat(frames, ignore_index=True)
    return clean_climate_data(combined)
