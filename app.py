from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st

from core.azure_client import azure_is_configured
from core.orchestrator import ClimateOrchestrator
from utils.export_helpers import to_pretty_json
from utils.preprocessing import clean_climate_data, combine_csv_files, validate_schema
from utils.visualizations import anomaly_overlay_chart, correlation_heatmap, line_chart, monthly_bar_chart

st.set_page_config(page_title="Climate Data Explorer", layout="wide", page_icon="🌦️")

CSS = """
<style>
    .block-container {max-width: 1400px; padding-top: 1.2rem; padding-bottom: 2rem;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg, #0F172A 0%, #111827 100%);}
    [data-testid="stSidebar"] * {color: #E5E7EB;}
    .hero {
        background: linear-gradient(135deg, rgba(79,70,229,.08), rgba(14,165,233,.10));
        border: 1px solid rgba(15,23,42,.08);
        border-radius: 24px; padding: 1.35rem 1.4rem; margin-bottom: 1rem;
    }
    .hero h1 {margin: 0; font-size: 2rem;}
    .hero p {margin: .35rem 0 0 0; color: #475569;}
    .metric-card {
        background: #FFFFFF; border: 1px solid rgba(15,23,42,.08); border-radius: 20px;
        padding: 1rem 1.1rem; box-shadow: 0 12px 36px rgba(15,23,42,.06);
    }
    .section-card {
        background: #FFFFFF; border: 1px solid rgba(15,23,42,.08); border-radius: 22px;
        padding: 1rem 1.1rem; box-shadow: 0 10px 28px rgba(15,23,42,.05);
    }
    .pill {
        display: inline-block; padding: .3rem .65rem; border-radius: 999px;
        background: rgba(79,70,229,.09); color: #4338CA; font-size: .85rem; margin-right: .35rem;
    }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

DEFAULT_FILES = [
    "data/export_combined.csv",
]


def load_default_dataset() -> pd.DataFrame:
    root = Path(__file__).parent
    full_paths = [root / path for path in DEFAULT_FILES if (root / path).exists()]
    if not full_paths:
        return pd.DataFrame()
    return combine_csv_files([str(full_paths[0])]) if len(full_paths) == 1 else combine_csv_files([str(p) for p in full_paths])


def apply_filters(df: pd.DataFrame, start_date, end_date, selected_metrics: List[str]) -> pd.DataFrame:
    filtered = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)].copy()
    keep = ["date", "year", "month", "month_name", "quarter", "temp_range", "rain_flag", "high_wind_flag", "tavg_7d", "prcp_7d"]
    keep += [metric for metric in selected_metrics if metric in filtered.columns]
    keep = [col for col in keep if col in filtered.columns]
    return filtered[keep].copy()


with st.sidebar:
    st.markdown("## Climate Data Explorer")
    st.caption("Multi-Agent Weather Intelligence")
    uploaded_files = st.file_uploader(
        "Upload one or more CSV files",
        type=["csv"],
        accept_multiple_files=True,
        help="Use this to replace or extend the bundled Heathrow dataset.",
    )
    user_question = st.text_area(
        "Analysis goal",
        value="Analyse seasonal climate patterns, detect anomalies, and produce practical planning recommendations.",
        height=120,
    )
    anomaly_sensitivity = st.slider("Anomaly sensitivity (z-score)", min_value=2.0, max_value=4.0, value=2.5, step=0.1)
    run_analysis = st.button("Run Multi-Agent Analysis", use_container_width=True)

st.markdown(
    """
    <div class="hero">
        <span class="pill">Production-grade Streamlit UI</span>
        <span class="pill">Sequential Multi-Agent Pipeline</span>
        <span class="pill">Azure OpenAI Ready</span>
        <h1>Climate Data Explorer</h1>
        <p>Explore London Heathrow climate trends, anomalies, and action-oriented recommendations through a modern SaaS-style dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if uploaded_files:
    raw_df = pd.concat([pd.read_csv(file) for file in uploaded_files], ignore_index=True)
    df = clean_climate_data(raw_df)
else:
    df = load_default_dataset()

if df.empty:
    st.error("No dataset found. Upload at least one CSV or place export_combined.csv in the data folder.")
    st.stop()

valid, missing_cols = validate_schema(df)
if not valid:
    st.error(f"Dataset is missing required columns: {missing_cols}")
    st.stop()

min_date = df["date"].min().date()
max_date = df["date"].max().date()

col_a, col_b, col_c = st.columns([1, 1, 2])
with col_a:
    start_date = st.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
with col_b:
    end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)
with col_c:
    selected_metrics = st.multiselect(
        "Metrics",
        options=["tavg", "tmin", "tmax", "prcp", "wspd", "wpgt", "pres", "tsun", "temp_range"],
        default=["tavg", "prcp", "wspd", "pres", "tsun"],
    )

filtered_df = apply_filters(df, start_date, end_date, selected_metrics)

cards = st.columns(6)
metrics = {
    "Records": f"{len(filtered_df):,}",
    "Years": f"{filtered_df['year'].nunique()}",
    "Avg temp": f"{filtered_df['tavg'].mean():.1f} °C",
    "Total rain": f"{filtered_df['prcp'].sum():.1f} mm",
    "Avg pressure": f"{filtered_df['pres'].mean():.1f} hPa",
    "Avg wind": f"{filtered_df['wspd'].mean():.1f} km/h",
}
for col, (label, value) in zip(cards, metrics.items()):
    with col:
        st.markdown(f'<div class="metric-card"><div style="color:#64748B;font-size:.9rem;">{label}</div><div style="font-size:1.45rem;font-weight:700;">{value}</div></div>', unsafe_allow_html=True)

if run_analysis or "analysis_payload" not in st.session_state:
    orchestrator = ClimateOrchestrator()
    with st.spinner("Running agents..."):
        payload = orchestrator.run(filtered_df.copy(), user_question)
    st.session_state["analysis_payload"] = payload
else:
    payload = st.session_state["analysis_payload"]

analysis_payload = st.session_state.get("analysis_payload", {})

# adjust anomaly chart using selected sensitivity in UI for display purposes
from core.tools import detect_outliers
anomaly_payload = detect_outliers(filtered_df, "tavg", anomaly_sensitivity)
anomaly_dates = [item["date"] for item in anomaly_payload.get("anomalies", [])]

overview_tab, trends_tab, anomalies_tab, report_tab, json_tab = st.tabs([
    "Overview", "Trends", "Anomalies", "Agent Report", "JSON Output"
])

with overview_tab:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.pyplot(line_chart(filtered_df, "tavg", "Daily Average Temperature"), clear_figure=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.pyplot(monthly_bar_chart(filtered_df, "prcp", "Monthly Rainfall Totals", agg="sum"), clear_figure=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.pyplot(monthly_bar_chart(filtered_df, "tsun", "Monthly Sunshine Duration", agg="sum"), clear_figure=True)
    st.markdown('</div>', unsafe_allow_html=True)

with trends_tab:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.pyplot(monthly_bar_chart(filtered_df, "tavg", "Monthly Average Temperature", agg="mean"), clear_figure=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        heatmap_cols = [col for col in ["tavg", "prcp", "wspd", "pres", "tsun", "temp_range"] if col in filtered_df.columns]
        st.pyplot(correlation_heatmap(filtered_df, heatmap_cols, "Correlation Heatmap"), clear_figure=True)
        st.markdown('</div>', unsafe_allow_html=True)

with anomalies_tab:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.pyplot(anomaly_overlay_chart(filtered_df, "tavg", anomaly_dates, "Temperature Anomaly Overlay"), clear_figure=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Top anomalies")
        if anomaly_payload.get("anomalies"):
            st.dataframe(pd.DataFrame(anomaly_payload["anomalies"]), use_container_width=True, hide_index=True)
        else:
            st.info("No anomalies found at the current sensitivity level.")
        st.markdown('</div>', unsafe_allow_html=True)

with report_tab:
    for section_name in ["loader", "trend", "anomalies", "policy"]:
        section = analysis_payload.get(section_name, {})
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader(section_name.replace("_", " ").title())
        if "summary" in section:
            st.write(section["summary"])
        elif "raw" in section:
            st.write(section["raw"])
        for key in ["bullets", "risks", "recommendations"]:
            values = section.get(key, [])
            if values:
                st.markdown(f"**{key.title()}**")
                for item in values:
                    st.write(f"- {item}")
        st.markdown('</div>', unsafe_allow_html=True)

with json_tab:
    report_json = {
        "dataset": {
            "rows": int(len(filtered_df)),
            "date_start": str(filtered_df["date"].min().date()),
            "date_end": str(filtered_df["date"].max().date()),
            "azure_configured": azure_is_configured(),
        },
        "analysis": analysis_payload,
        "display_anomalies": anomaly_payload,
    }
    st.code(to_pretty_json(report_json), language="json")
    st.download_button(
        "Download JSON Report",
        data=to_pretty_json(report_json),
        file_name="climate_report.json",
        mime="application/json",
    )
    st.download_button(
        "Download Cleaned Dataset",
        data=filtered_df.to_csv(index=False),
        file_name="cleaned_climate_dataset.csv",
        mime="text/csv",
    )
