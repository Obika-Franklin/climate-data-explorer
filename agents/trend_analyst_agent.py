from __future__ import annotations

from agents.base_agent import Agent
from utils.helpers import safe_json_dumps


class TrendAnalystAgent(Agent):
    def __init__(self):
        super().__init__(
            name="TrendAnalystAgent",
            system_prompt=(
                "You are a climate trend analysis agent. Explain temperature, rainfall, sunshine, "
                "and wind patterns in clear, business-style language for a dashboard audience."
            ),
        )

    def build_user_message(self, context: dict) -> str:
        return (
            "Analyse the dataset summary and monthly aggregates. Identify the most useful climate trends.\n\n"
            f"{safe_json_dumps(context)}"
        )
