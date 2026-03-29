"""Sequential orchestrator for the climate multi-agent workflow."""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from agents.anomaly_detector_agent import AnomalyDetectorAgent
from agents.data_loader_agent import DataLoaderAgent
from agents.policy_advisor_agent import PolicyAdvisorAgent
from agents.trend_analyst_agent import TrendAnalystAgent
from core.azure_client import get_azure_client, get_deployment_name
from core.safety import bounded_run


class ClimateOrchestrator:
    def __init__(self):
        client = get_azure_client()
        deployment_name = get_deployment_name()
        self.data_loader = DataLoaderAgent(client, deployment_name)
        self.trend_analyst = TrendAnalystAgent(client, deployment_name)
        self.anomaly_detector = AnomalyDetectorAgent(client, deployment_name)
        self.policy_advisor = PolicyAdvisorAgent(client, deployment_name)

    def run(self, df: pd.DataFrame, user_question: str) -> Dict[str, Any]:
        loader = bounded_run(self.data_loader.run, df, user_question, {})
        trend = bounded_run(self.trend_analyst.run, df, user_question, {"loader": loader})
        anomalies = bounded_run(self.anomaly_detector.run, df, user_question, {"loader": loader, "trend": trend})
        policy = bounded_run(
            self.policy_advisor.run,
            df,
            user_question,
            {"loader": loader, "trend": trend, "anomalies": anomalies},
        )
        return {
            "loader": loader,
            "trend": trend,
            "anomalies": anomalies,
            "policy": policy,
        }
