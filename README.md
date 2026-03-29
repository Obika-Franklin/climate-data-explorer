# Climate Data Explorer

A production-ready **multi-agent GenAI climate intelligence dashboard** built with **Streamlit**, **Azure OpenAI**, and a **sequential multi-agent workflow**.

## What this project does

This project analyzes historical weather data from **London Heathrow weather station** and turns it into:

- a modern SaaS-style dashboard
- seasonal trend insights
- anomaly detection
- practical recommendations
- downloadable JSON and CSV outputs

## Project requirements coverage

This starter pack satisfies the brief as follows:

- **Real dataset**: bundled Heathrow climate data combined across multiple CSV files
- **At least 3 specialised agents**: `DataLoaderAgent`, `TrendAnalystAgent`, `AnomalyDetectorAgent`, `PolicyAdvisorAgent`
- **At least 1 multi-agent pattern**: sequential pipeline via `ClimateOrchestrator`
- **Azure OpenAI**: client helper wired for Azure OpenAI v1-style endpoint setup
- **At least 2 tools**: `compute_summary_stats`, `detect_outliers`, `generate_chart_metadata`
- **Final structured output**: JSON report + visualizations
- **Safety**: max-iteration guard and graceful error envelopes
- **Bonus deployment path**: GitHub + Streamlit Community Cloud ready

## Folder structure

```text
climate-data-explorer/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── data/
│   └── export_combined.csv
├── agents/
│   ├── base_agent.py
│   ├── data_loader_agent.py
│   ├── trend_analyst_agent.py
│   ├── anomaly_detector_agent.py
│   └── policy_advisor_agent.py
├── core/
│   ├── azure_client.py
│   ├── orchestrator.py
│   ├── prompts.py
│   ├── safety.py
│   └── tools.py
└── utils/
    ├── export_helpers.py
    ├── preprocessing.py
    └── visualizations.py
```

## How the agents work

### 1. DataLoaderAgent
- validates schema
- cleans and enriches the dataset
- summarizes coverage, missingness, and engineered features

### 2. TrendAnalystAgent
- explains seasonal temperature, rainfall, sunshine, pressure, and wind patterns
- produces interpretable climate insights

### 3. AnomalyDetectorAgent
- detects unusual temperature, rainfall, wind, and pressure events
- ranks top anomaly days

### 4. PolicyAdvisorAgent
- turns findings into plain-English recommendations
- useful for operations, planning, and public communication

## Multi-agent pattern

This project uses a **sequential pipeline**:

```text
DataLoaderAgent → TrendAnalystAgent → AnomalyDetectorAgent → PolicyAdvisorAgent
```

## Azure OpenAI setup

Add the following secrets in your local `.streamlit/secrets.toml` or in **Streamlit Community Cloud**:

```toml
AZURE_OPENAI_API_KEY = "your_key"
AZURE_OPENAI_ENDPOINT = "https://your-resource-name.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT = "your_deployment_name"
```

The app will still run without Azure configured, but agent outputs will fall back to deterministic heuristic mode for demo/testing.

## Local setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

## Streamlit Community Cloud deployment

### 1. Push the project to GitHub

Initialize git and push to your repository.

### 2. Deploy on Streamlit

- Go to Streamlit Community Cloud
- Click **New app**
- Select your GitHub repo
- Set **Main file path** to `app.py`
- Add your Azure secrets in the app settings
- Deploy

## Suggested demo flow for presentation

1. Open the app
2. Show the Heathrow combined dataset metrics
3. Run the multi-agent analysis
4. Walk through overview charts
5. Show the anomaly overlay
6. Open the agent report
7. Download the JSON report

## Notes on the bundled data

This starter pack includes a combined Heathrow dataset spanning:

- 2023
- 2024
- 2025
- 2026 (partial)

That gives you enough rows to satisfy the minimum dataset size requirement.

## Suggested next upgrades

- add richer prompt engineering for each agent
- add user-selectable anomaly metric in the sidebar
- add PDF report export
- add a small chat interface for follow-up questions
- add unit tests before final submission
