from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from agents.anomaly_detector_agent import AnomalyDetectorAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.report_writer_agent import ReportWriterAgent
from agents.trend_analyst_agent import TrendAnalystAgent
from tools.chart_tools import plot_anomalies, plot_monthly_rainfall, plot_monthly_temperature
from tools.data_tools import detect_anomalies, get_climate_summary, get_monthly_trends
from utils.azure_client import azure_config_available
from utils.preprocessing import load_and_combine_csvs


st.set_page_config(
    page_title="Heathrow Climate Explorer",
    page_icon="🌦️",
    layout="wide",
)


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


def build_fallback_report(summary: dict, anomalies: dict, monthly_trends: dict) -> str:
    metrics = summary.get("metrics", {})
    temp_mean = metrics.get("tavg", {}).get("mean", "N/A")
    wind_mean = metrics.get("wspd", {}).get("mean", "N/A")
    trend_records = monthly_trends.get("monthly_trends", [])

    wettest_month = "N/A"
    warmest_month = "N/A"

    if trend_records:
        try:
            wettest_month = max(
                trend_records,
                key=lambda x: x.get("prcp", float("-inf")),
            ).get("month", "N/A")
            warmest_month = max(
                trend_records,
                key=lambda x: x.get("tavg", float("-inf")),
            ).get("month", "N/A")
        except Exception:
            pass

    return f"""
### Climate Report

**Dataset Summary**
- Records: {summary.get('records', 'N/A')}
- Period: {summary.get('date_range', {}).get('start', 'N/A')} to {summary.get('date_range', {}).get('end', 'N/A')}

**Trend Insights**
- Average temperature across the selected range is **{temp_mean} °C**.
- Average wind speed across the selected range is **{wind_mean} km/h**.
- The warmest month in the current selection appears to be **{warmest_month}**.
- The wettest month in the current selection appears to be **{wettest_month}**.

**Anomaly Insights**
- Temperature anomalies detected: **{anomalies.get('counts', {}).get('tavg', 0)}**
- Rainfall anomalies detected: **{anomalies.get('counts', {}).get('prcp', 0)}**
- Wind anomalies detected: **{anomalies.get('counts', {}).get('wspd', 0)}**

**Final Interpretation**
- The filtered Heathrow dataset shows seasonal variability in temperature and rainfall.
- Unusual events are highlighted through z-score anomaly detection and should be checked against the anomaly chart for context.
- This fallback summary is generated locally when Azure OpenAI output is unavailable.
"""


def run_multi_agent_pipeline(filtered_df, threshold: float) -> dict:
    """
    True LLM-agent flow:
    - Agents use Azure OpenAI through BaseAgent
    - The LLM can choose to call tools
    - Tools are executed through the registry below
    """
    tool_registry = {
        "get_climate_summary": lambda: get_climate_summary(filtered_df),
        "detect_anomalies": lambda z_threshold: detect_anomalies(filtered_df, z_threshold=z_threshold),
        "get_monthly_trends": lambda: get_monthly_trends(filtered_df),
    }

    orchestrator = OrchestratorAgent()
    trend_agent = TrendAnalystAgent()
    anomaly_agent = AnomalyDetectorAgent()
    report_agent = ReportWriterAgent()

    orchestration = orchestrator.run(
        user_prompt=(
            f"Analyze the currently filtered Heathrow climate dataset. "
            f"Use tools to inspect the data and prepare a concise structured handoff for specialist agents. "
            f"The anomaly threshold to consider is {threshold}."
        ),
        tool_registry=tool_registry,
    )

    trend_result = trend_agent.run(
        user_prompt=(
            "Using the available tools, analyze the filtered Heathrow climate dataset. "
            "Focus on temperature behavior, rainfall patterns, wind speed, pressure, sunshine, "
            "seasonality, and any visible month-to-month structure."
        ),
        tool_registry=tool_registry,
    )

    anomaly_result = anomaly_agent.run(
        user_prompt=(
            f"Using the available tools, detect and interpret unusual climate observations in the filtered "
            f"Heathrow dataset with z-threshold {threshold}. Explain whether the anomalies seem isolated, "
            f"clustered, seasonal, or operationally meaningful."
        ),
        tool_registry=tool_registry,
    )

    report_result = report_agent.run(
        user_prompt=(
            "Write a structured final report for a non-technical audience using the specialist findings below.\n\n"
            f"Orchestrator Handoff:\n{orchestration.get('content', '')}\n\n"
            f"Trend Analyst Output:\n{trend_result.get('content', '')}\n\n"
            f"Anomaly Detector Output:\n{anomaly_result.get('content', '')}\n\n"
            "Use the sections: Dataset Summary, Trend Insights, Anomaly Insights, Final Interpretation."
        ),
        tool_registry=tool_registry,
    )

    return {
        "orchestrator": orchestration,
        "trend_analyst": trend_result,
        "anomaly_detector": anomaly_result,
        "report_writer": report_result,
    }


def main():
    inject_css()
    df = get_data()

    st.markdown(
        f"""
        <div class="hero">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap;">
                <div class="badge">{'🟢 AI Ready' if azure_config_available() else '🟡 AI Disabled (Local Mode)'}</div>
                <a href="https://www.linkedin.com/in/franklinobika/" target="_blank">
                    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg"
                         width="24" height="24">
                </a>
            </div>
            <h1 style="margin:0.7rem 0 0.2rem 0;">Heathrow Climate Explorer</h1>
            <p class="muted" style="margin:0;">
                A production-style multi-agent climate dashboard for trend analysis,
                anomaly detection, and AI reporting from London Heathrow climate data.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.title("Controls")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

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

    filtered_df = df[
        (df["date"].dt.date >= start_date) &
        (df["date"].dt.date <= end_date)
    ].copy()

    summary = get_climate_summary(filtered_df)
    anomalies = detect_anomalies(filtered_df, z_threshold=threshold)
    monthly_trends = get_monthly_trends(filtered_df)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card(
            "🌡 Avg Temp",
            f"{summary['metrics'].get('tavg', {}).get('mean', 'N/A')} °C",
            "Daily average across selection",
        )
    with col2:
        render_metric_card(
            "🌧 Total Rainfall",
            f"{round(filtered_df['prcp'].fillna(0).sum(), 1)} mm" if "prcp" in filtered_df.columns else "N/A",
            "Cumulative precipitation",
        )
    with col3:
        render_metric_card(
            "💨 Avg Wind Speed",
            f"{summary['metrics'].get('wspd', {}).get('mean', 'N/A')} km/h",
            "Mean daily wind speed",
        )
    with col4:
        render_metric_card(
            "☀ Total Sunshine",
            f"{int(filtered_df['tsun'].fillna(0).sum())} min" if "tsun" in filtered_df.columns else "N/A",
            "Sum of recorded sunshine",
        )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Overview", "Trends", "Anomalies", "AI Insights"]
    )

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

        with st.expander("Monthly Trend Data"):
            st.dataframe(
                monthly_trends.get("monthly_trends", []),
                use_container_width=True,
            )

    with tab3:
        st.subheader("Detected Anomalies")
        st.pyplot(plot_anomalies(filtered_df, threshold=threshold), use_container_width=True)
        st.json(anomalies)

    with tab4:
        st.subheader("Multi-Agent AI Insights")
        st.markdown(
            """
### 🤖 Multi-Agent System
- **OrchestratorAgent** → decides what information is needed and coordinates the workflow  
- **TrendAnalystAgent** → interprets climate patterns and seasonal behavior  
- **AnomalyDetectorAgent** → identifies and explains unusual weather events  
- **ReportWriterAgent** → synthesizes specialist outputs into a final report  
"""
        )
        st.warning("⚠️ AI outputs may be inaccurate. Always verify insights with charts and raw data.")

        if run_agents:
            if not azure_config_available():
                st.info("Azure OpenAI is not configured, so the app will show a local fallback report.")
                final_report = build_fallback_report(summary, anomalies, monthly_trends)
                agent_outputs = {
                    "orchestrator": {"status": "fallback", "content": "Azure unavailable."},
                    "trend_analyst": {"status": "fallback", "content": "Azure unavailable."},
                    "anomaly_detector": {"status": "fallback", "content": "Azure unavailable."},
                    "report_writer": {"status": "fallback", "content": final_report},
                }
            else:
                try:
                    with st.spinner("Running multi-agent analysis with Azure OpenAI..."):
                        agent_outputs = run_multi_agent_pipeline(filtered_df, threshold)
                    st.success("Analysis complete ✅")
                except Exception as e:
                    st.error(f"AI pipeline error: {e}")
                    final_report = build_fallback_report(summary, anomalies, monthly_trends)
                    agent_outputs = {
                        "orchestrator": {"status": "failed", "content": str(e)},
                        "trend_analyst": {"status": "failed", "content": str(e)},
                        "anomaly_detector": {"status": "failed", "content": str(e)},
                        "report_writer": {"status": "fallback", "content": final_report},
                    }

            st.markdown("#### Agent Outputs")
            for key, value in agent_outputs.items():
                with st.expander(key.replace("_", " ").title(), expanded=(key == "report_writer")):
                    st.json(value)

            final_report = agent_outputs.get("report_writer", {}).get("content")
            if not final_report:
                final_report = build_fallback_report(summary, anomalies, monthly_trends)

            st.subheader("📊 Final Insight")
            st.markdown(final_report)

            report_data = {
                "dataset_period": summary["date_range"],
                "records": summary["records"],
                "metrics": summary["metrics"],
                "monthly_trends": monthly_trends,
                "anomalies": anomalies,
                "agents": agent_outputs,
                "ai_report": final_report,
            }

            st.download_button(
                "📥 Download Full Report",
                data=json.dumps(report_data, indent=2, default=str),
                file_name="heathrow_climate_report.json",
                mime="application/json",
            )
        else:
            st.info("Click **🚀 Run AI Analysis** in the sidebar to generate the multi-agent summary.")
            st.markdown(build_fallback_report(summary, anomalies, monthly_trends))

    st.markdown("---")
    st.markdown(
        """
<div style="display:flex; justify-content:space-between; align-items:center;">
    <span style="color:#64748b;">Built with Streamlit • Multi-Agent AI • Azure OpenAI</span>
    <a href="https://www.linkedin.com/in/franklinobika/" target="_blank">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg"
             width="24" height="24">
    </a>
</div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
