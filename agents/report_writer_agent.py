from __future__ import annotations

from agents.base_agent import Agent
from utils.helpers import safe_json_dumps


class ReportWriterAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ReportWriterAgent",
            system_prompt=(
                "You are a climate reporting agent. Produce a polished, executive-style summary with "
                "sections for data quality, key trends, anomaly findings, and recommended next steps."
            ),
        )

    def build_user_message(self, context: dict) -> str:
        return (
            "Create a final climate report from these agent outputs. Use short sections and plain English.\n\n"
            f"{safe_json_dumps(context)}"
        )
