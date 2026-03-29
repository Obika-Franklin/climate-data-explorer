# Heathrow Climate Explorer (Multi-Agent AI Dashboard)

## Overview

The **Heathrow Climate Explorer** is a production-style data science dashboard built with **Streamlit** and **Azure OpenAI**. It uses a **multi-agent AI system** to analyse real-world weather data from London Heathrow, detect anomalies, and generate structured climate insights.

This project demonstrates how **Generative AI agents** can be orchestrated to solve real-world data analysis problems in a clear, interactive, and scalable way.

---

## Key Features

* 📊 Interactive climate dashboard (Streamlit UI)
* 🤖 Multi-agent AI system (4 specialised agents)
* 📈 Trend analysis (temperature, rainfall, wind, sunshine)
* ⚠️ Anomaly detection using z-score
* 🧠 AI-generated climate insights (Azure OpenAI)
* 📥 Downloadable structured JSON reports
* 🧩 Modular architecture (agents, tools, utils)

---

## Multi-Agent Architecture

This project implements a **sequential multi-agent pipeline**:

1. **DataLoaderAgent**

   * Loads, validates, and summarises the dataset

2. **TrendAnalystAgent**

   * Analyses seasonal patterns and long-term trends

3. **AnomalyDetectorAgent**

   * Identifies extreme or unusual weather events

4. **ReportWriterAgent**

   * Combines outputs into a structured AI-generated report

---

## Tools Used

* **Climate Summary Tool**
  Computes statistics such as averages, min/max values, missing data, and date coverage

* **Anomaly Detection Tool**
  Detects unusual observations using z-score thresholding

---

## Dataset

* Source: London Heathrow Weather Data
* Format: CSV (combined from multiple files)
* Records: 1,000+ daily observations
* Features include:

  * Temperature (avg, min, max)
  * Rainfall
  * Wind speed
  * Pressure
  * Sunshine duration

---

## Tech Stack

* **Python**
* **Streamlit**
* **Pandas / NumPy**
* **Matplotlib**
* **Azure OpenAI (LLM integration)**

---

## Live App

👉 https://climate-data-explorer-blmsj4f7skw6x8zhqycg3f.streamlit.app/

---

## 📸 Screenshot
<img width="1901" height="825" alt="image" src="https://github.com/user-attachments/assets/cc285057-1e8a-46cb-b2a1-0638c8ff0ee1" />



---

## Environment Setup

To run locally, create a `.streamlit/secrets.toml` file:

```toml
AZURE_OPENAI_API_KEY="your_api_key"
AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT="your_deployment_name"
AZURE_OPENAI_API_VERSION="2024-02-01"
```

---

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Safety Considerations

* AI-generated insights may be inaccurate or incomplete
* Users are advised to verify results using charts and raw data
* The system includes fallback logic when AI is unavailable

---

## Project Structure

```
climate-data-explorer/
│
├── app.py
├── requirements.txt
├── README.md
├── data/
├── agents/
├── tools/
├── utils/
└── .streamlit/
```

---

## 🎓 Learning Outcomes

This project demonstrates:

* Multi-agent system design
* LLM integration with Azure OpenAI
* Data analysis and visualization
* Building production-grade dashboards with Streamlit
* Structuring AI workflows for real-world applications

---

## Acknowledgements

* Streamlit for rapid dashboard development
* Azure OpenAI for LLM capabilities
* Public climate datasets for real-world data

---

## Connect with me

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Franklin%20Obika-blue?logo=linkedin&style=for-the-badge)](https://www.linkedin.com/in/franklinobika)

---


