# Heathrow Climate Explorer

A simple, production-style **multi-agent GenAI dashboard** built with **Streamlit**, **Azure OpenAI**, **pandas**, and **matplotlib**.

It combines multiple London Heathrow weather CSV files, analyses climate trends, detects anomalies, and generates an AI-assisted climate report.

## Project requirements covered

- Real dataset with more than 500 rows
- 3+ specialised agents implemented as classes
- Sequential multi-agent pipeline
- Azure OpenAI client used as the LLM client
- 2 custom tools
- Final structured output and visualisations
- Safety guard with max iterations and graceful fallback handling
- Ready for Streamlit Community Cloud deployment

## Agents

- **DataLoaderAgent**: reviews data quality and coverage
- **TrendAnalystAgent**: explains monthly climate patterns
- **AnomalyDetectorAgent**: interprets unusual events
- **ReportWriterAgent**: generates the final report

## Tools

- `get_climate_summary(df)`
- `detect_anomalies(df, z_threshold=2.0)`

## Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit secrets

Create `.streamlit/secrets.toml` locally, or paste the same values into Streamlit Cloud Secrets:

```toml
AZURE_OPENAI_API_KEY="your_key_here"
AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT="your_deployment_name"
AZURE_OPENAI_API_VERSION="2024-02-01"
```

## Recommended GitHub upload order

1. Upload the full project folder
2. Make sure `app.py` is in the root
3. Make sure `requirements.txt` is in the root
4. Do **not** upload secrets
5. Deploy from GitHub to Streamlit Community Cloud

## Suggested demo flow

1. Open the Overview tab
2. Show the KPI cards
3. Show the monthly charts
4. Open Anomalies
5. Run the multi-agent workflow
6. Download the final structured summary
