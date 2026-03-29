from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from agents.base_agent import Agent
from core.prompts import POLICY_ADVISOR_PROMPT


class PolicyAdvisorAgent(Agent):
    def __init__(self, client=None, deployment_name: str | None = None):
        super().__init__("PolicyAdvisorAgent", POLICY_ADVISOR_PROMPT, client, deployment_name)

    def heuristic(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        trend = context.get("trend", {})
        anomalies = context.get("anomalies", {})
        return {
            "status": "ok",
            "agent": self.name,
            "summary": "Operational planning should rely on seasonal averages for baseline expectations and anomaly alerts for short-term caution.",
            "bullets": [
                "Use sunshine and temperature jointly when advising outdoor activity or tourism windows.",
                "Escalate communication on high-rainfall and high-wind anomaly days.",
                "Treat low-pressure extremes as attention points for travel and operations messaging.",
            ],
            "risks": [
                "Users may overgeneralise from one extreme day if the dashboard does not separate climate pattern from event alerting.",
            ],
            "recommendations": [
                "Add seasonal planning notes to the dashboard overview.",
                "Provide a downloadable JSON report for decision support workflows.",
                "Use anomaly tables for incident-style review instead of long narrative text.",
            ],
            "inputs_used": {
                "trend_available": bool(trend),
                "anomalies_available": bool(anomalies),
            },
        }
