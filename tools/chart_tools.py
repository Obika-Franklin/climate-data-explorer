from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


plt.rcParams["figure.facecolor"] = "white"
plt.rcParams["axes.facecolor"] = "white"


def plot_monthly_temperature(df: pd.DataFrame):
    monthly = df.groupby("year_month", as_index=False)["tavg"].mean()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(monthly["year_month"], monthly["tavg"], linewidth=2)
    ax.set_title("Monthly Average Temperature")
    ax.set_xlabel("Month")
    ax.set_ylabel("Temperature (°C)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig


def plot_monthly_rainfall(df: pd.DataFrame):
    monthly = df.groupby("year_month", as_index=False)["prcp"].sum()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(monthly["year_month"], monthly["prcp"])
    ax.set_title("Monthly Rainfall")
    ax.set_xlabel("Month")
    ax.set_ylabel("Rainfall (mm)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.25, axis="y")
    fig.tight_layout()
    return fig


def plot_anomalies(df: pd.DataFrame, threshold: float = 2.0):
    series = df["tavg"].dropna()
    std = series.std(ddof=0)
    mean = series.mean()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["date"], df["tavg"], linewidth=1.6, label="Daily Avg Temp")
    if std and not pd.isna(std):
        z_scores = (df["tavg"] - mean) / std
        flagged = df.loc[z_scores.abs() >= threshold]
        ax.scatter(flagged["date"], flagged["tavg"], s=40, label="Anomalies")
    ax.set_title("Temperature Anomalies")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig
