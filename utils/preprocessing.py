from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


CLIMATE_COLUMNS = ["date", "tavg", "tmin", "tmax", "prcp", "wspd", "wpgt", "pres", "tsun"]


def load_and_combine_csvs(file_paths: Iterable[str | Path]) -> pd.DataFrame:
    frames = []
    for path in file_paths:
        df = pd.read_csv(path)
        frames.append(df)

    if not frames:
        raise ValueError("No CSV files were found in the data folder.")

    combined = pd.concat(frames, ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"], errors="coerce")
    combined = combined.dropna(subset=["date"]).sort_values("date").drop_duplicates(subset=["date"])

    for col in ["snow", "wdir"]:
        if col in combined.columns:
            combined = combined.drop(columns=col)

    for col in CLIMATE_COLUMNS:
        if col != "date" and col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce")

    combined["year"] = combined["date"].dt.year
    combined["month"] = combined["date"].dt.month
    combined["month_name"] = combined["date"].dt.strftime("%b")
    combined["year_month"] = combined["date"].dt.to_period("M").astype(str)

    return combined.reset_index(drop=True)
