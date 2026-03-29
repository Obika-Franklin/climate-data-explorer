from __future__ import annotations

from agents.base_agent import Agent
from utils.helpers import safe_json_dumps


class DataLoaderAgent(Agent):
    def __init__(self):
        super().__init__(
            name="DataLoaderAgent",
            system_prompt=(
                "You are a climate data preparation agent. Inspect climate data summaries, "
                "comment on data quality, coverage, and readiness for downstream analysis. "
                "Keep the response concise and structured."
            ),
        )

    def build_user_message(self, context: dict) -> str:
        return (
            "Review this climate dataset summary and provide a short data quality assessment.\n\n"
            f"{safe_json_dumps(context)}"
        )
