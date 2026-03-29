"""Matplotlib chart builders."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def line_chart(df: pd.DataFrame, y: str, title: str):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["date"], df[y], linewidth=1.8)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(y)
    ax.grid(alpha=0.25)
    fig.autofmt_xdate()
    return fig


def monthly_bar_chart(df: pd.DataFrame, y: str, title: str, agg: str = "mean"):
    monthly = df.groupby("month_name", sort=False)[y].sum() if agg == "sum" else df.groupby("month_name", sort=False)[y].mean()
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = monthly.reindex([m for m in month_order if m in monthly.index])
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(monthly.index, monthly.values)
    ax.set_title(title)
    ax.set_xlabel("Month")
    ax.set_ylabel(y)
    ax.grid(axis="y", alpha=0.25)
    return fig


def correlation_heatmap(df: pd.DataFrame, columns: list[str], title: str):
    corr = df[columns].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(corr.values)
    ax.set_xticks(range(len(columns)))
    ax.set_yticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=45, ha="right")
    ax.set_yticklabels(columns)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return fig


def anomaly_overlay_chart(df: pd.DataFrame, metric: str, anomaly_dates: list[str], title: str):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["date"], df[metric], linewidth=1.6)
    anomaly_df = df[df["date"].dt.strftime("%Y-%m-%d").isin(anomaly_dates)]
    if not anomaly_df.empty:
        ax.scatter(anomaly_df["date"], anomaly_df[metric], s=50)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(metric)
    ax.grid(alpha=0.25)
    fig.autofmt_xdate()
    return fig
