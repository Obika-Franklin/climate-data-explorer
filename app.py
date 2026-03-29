from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from agents.anomaly_detector_agent import AnomalyDetectorAgent
from agents.data_loader_agent import DataLoaderAgent
from agents.report_writer_agent import ReportWriterAgent
from agents.trend_analyst_agent import TrendAnalystAgent
from tools.chart_tools import plot_anomalies, plot_monthly_rainfall, plot_monthly_temperature
from tools.data_tools import detect_anomalies, get_climate_summary
from utils.azure_client import azure_config_available
from utils.preprocessing import load_and_combine_csvs


st.set_page_config(page_title="Heathrow Climate Explorer", page_icon="🌦️", layout="wide")


@st.cache_data
def get_data():
    data_dir = Path(__file__).parent / "data"
    files = sorted(data_dir.glob("*.csv"))
    return load_and_combine_csvs(files)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .hero {
            padding: 1.25rem 1.4rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 20px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
            margin-bottom: 1rem;
        }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }
        .metric-card {
            background: white;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.04);
        }
        .muted {
            color: #475569;
        }
        .stButton > button {
            border-radius: 12px;
            font-weight: 600;
        }
        div[data-testid="stMetric"] {
            border-radius: 16px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="muted">{label}</div>
            <div style="font-size:1.8rem;font-weight:700;margin:0.25rem 0;">{value}</div>
            <div class="muted" style="font-size:0.9rem;">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_multi_agent_pipeline(summary: dict, anomalies: dict) -> dict:
    data_agent = DataLoaderAgent()
    trend_agent = TrendAnalystAgent()
    anomaly_agent = AnomalyDetectorAgent()
    report_agent = ReportWriterAgent()

    data_result = data_agent.run(summary)
    trend_result = trend_agent.run(summary)
    anomaly_result = anomaly_agent.run(anomalies)

    report_context = {
        "data_quality": data_result,
        "trend_analysis": trend_result,
        "anomaly_analysis": anomaly_result,
        "summary": summary,
        "anomalies": anomalies,
    }
    report_result = report_agent.run(report_context)

    return {
        "data_loader": data_result,
        "trend_analyst": trend_result,
        "anomaly_detector": anomaly_result,
        "report_writer": report_result,
    }


def build_fallback_report(summary: dict, anomalies: dict) -> str:
    metrics = summary["metrics"]
    return f"""
### Climate Report

**Data coverage**
- Records: {summary['records']}
- Period: {summary['date_range']['start']} to {summary['date_range']['end']}

**Key trends**
- Average temperature: {metrics['tavg']['mean']} °C
- Total rainfall is distributed unevenly across months, with wetter and drier periods visible in the rainfall chart.
- Sunshine totals and wind speed fluctuate seasonally, which is expected in a daily weather dataset.

**Anomaly findings**
- Temperature anomalies: {anomalies['counts']['tavg']}
- Rainfall anomalies: {anomalies['counts']['prcp']}
- Wind anomalies: {anomalies['counts']['wspd']}

**Recommended next steps**
- Compare warm and wet periods month by month.
- Extend the dashboard with forecasting or station-to-station comparison.
- Validate AI summaries against charts before using them in reports.
"""


def main():
    inject_css()
    df = get_data()

    st.markdown(
        f"""
        <div class="hero">
            <div class="badge">{'🟢 AI Ready' if azure_config_available() else '🟡 AI Disabled (Local Mode)'}</div>
            <h1 style="margin:0.7rem 0 0.2rem 0;">Heathrow Climate Explorer</h1>
            <p class="muted" style="margin:0;">
                A production-style multi-agent dashboard for trend analysis,
                anomaly detection, and AI reporting from London Heathrow climate data.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.title("Controls")
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    selected_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    threshold = st.sidebar.slider(
        "Anomaly threshold (z-score)",
        min_value=1.5,
        max_value=3.5,
        value=2.0,
        step=0.1,
    )
    run_agents = st.sidebar.button("🚀 Run AI Analysis", type="primary")

    if isinstance(selected_range, tuple) and len(selected_range) == 2:
        start_date, end_date = selected_range
    else:
        start_date, end_date = min_date, max_date

    filtered_df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)].copy()
    summary = get_climate_summary(filtered_df)
    anomalies = detect_anomalies(filtered_df, z_threshold=threshold)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("🌡 Avg Temp", f"{summary['metrics']['tavg']['mean']} °C", "Daily average across selection")
    with col2:
        render_metric_card("🌧 Total Rainfall", f"{round(filtered_df['prcp'].sum(), 1)} mm", "Cumulative precipitation")
    with col3:
        render_metric_card("💨 Avg Wind Speed", f"{summary['metrics']['wspd']['mean']} km/h", "Mean daily wind speed")
    with col4:
        render_metric_card("☀ Total Sunshine", f"{int(filtered_df['tsun'].fillna(0).sum())} min", "Sum of recorded sunshine")

    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Trends", "Anomalies", "AI Insights"])

    with tab1:
        st.subheader("Dataset Overview")
        c1, c2 = st.columns([1, 1])
        with c1:
            st.write(
                {
                    "records": summary["records"],
                    "date_range": summary["date_range"],
                    "missing_values": summary["missing_values"],
                }
            )
        with c2:
            st.dataframe(filtered_df.tail(10), use_container_width=True)

        st.markdown("### Temperature Trend")
        st.pyplot(plot_monthly_temperature(filtered_df), use_container_width=True)

    with tab2:
        st.subheader("Climate Trends")
        st.pyplot(plot_monthly_temperature(filtered_df), use_container_width=True)
        st.pyplot(plot_monthly_rainfall(filtered_df), use_container_width=True)

    with tab3:
        st.subheader("Detected Anomalies")
        st.pyplot(plot_anomalies(filtered_df, threshold=threshold), use_container_width=True)
        st.json(anomalies)

    with tab4:
        st.subheader("Multi-Agent Report")
        st.caption("Safety note: AI summaries can be wrong. Cross-check conclusions with charts and raw data.")

        if run_agents:
            with st.spinner("Running multi-agent analysis..."):
                agent_outputs = run_multi_agent_pipeline(summary, anomalies)

            st.success("Analysis complete ✅")

            st.markdown("#### Agent Outputs")
            for key, value in agent_outputs.items():
                with st.expander(key.replace("_", " ").title(), expanded=(key == "report_writer")):
                    st.json(value)

            final_report = agent_outputs["report_writer"].get("content")
            if not final_report:
                final_report = build_fallback_report(summary, anomalies)

            st.subheader("📊 Final Insight")
            st.markdown(final_report)

            st.download_button(
                label="Download structured summary",
                data=json.dumps(
                    {"summary": summary, "anomalies": anomalies, "agents": agent_outputs},
                    indent=2,
                    default=str,
                ),
                file_name="climate_report.json",
                mime="application/json",
            )
        else:
            st.info("Click **🚀 Run AI Analysis** in the sidebar to generate the multi-agent summary.")
            st.markdown(build_fallback_report(summary, anomalies))

    st.markdown("---")
    st.caption("Built with Streamlit • Multi-Agent AI • Azure OpenAI")


if __name__ == "__main__":
    main()
