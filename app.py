import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from main import run_pipeline

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Climate Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #f5f5f5;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
with st.sidebar:
    st.title("⚙️ Controls")
    uploaded_file = st.file_uploader("Upload Dataset", type=["csv"])
    st.markdown("---")
    st.info("Upload a climate dataset or use the default Heathrow dataset.")

# ---------------- HEADER ---------------- #
st.title("🌍 Climate Data Explorer")
st.markdown("Advanced multi-agent system for climate trend analysis and anomaly detection.")

# ---------------- LOAD FILE ---------------- #
file = uploaded_file if uploaded_file else "data/export.csv"

if file:
    with st.spinner("Running multi-agent analysis..."):
        df, result = run_pipeline(file)

    # ---------------- KPI METRICS ---------------- #
    st.markdown("## 📊 Key Metrics")

    numeric_cols = df.select_dtypes(include="number").columns

    cols = st.columns(min(4, len(numeric_cols)))

    for i, col in enumerate(numeric_cols[:4]):
        with cols[i]:
            st.metric(label=col, value=round(df[col].mean(), 2))

    # ---------------- MAIN LAYOUT ---------------- #
    col1, col2 = st.columns([2, 1])

    # ----------- CHART SECTION ----------- #
    with col1:
        st.markdown("## 📈 Trend Analysis")

        selected_col = st.selectbox("Select variable", numeric_cols)

        fig, ax = plt.subplots()
        ax.plot(df[selected_col])
        ax.set_title(f"{selected_col} Over Time")
        ax.set_xlabel("Index")
        ax.set_ylabel(selected_col)

        st.pyplot(fig)

    # ----------- REPORT SECTION ----------- #
    with col2:
        st.markdown("## 🧠 AI Insights")

        st.markdown("### Trends")
        for k, v in result["trends"].items():
            st.write(f"**{k}:** {round(v, 2)}")

        st.markdown("### Anomalies")
        for k, v in result["anomalies"].items():
            st.write(f"**{k}:** {len(v)} anomalies detected")

    # ---------------- FULL REPORT ---------------- #
    st.markdown("## 📄 Full Report")
    st.json(result)

    # ---------------- DATA TABLE ---------------- #
    with st.expander("View Raw Data"):
        st.dataframe(df)

else:
    st.warning("Please upload a dataset to begin analysis.")
