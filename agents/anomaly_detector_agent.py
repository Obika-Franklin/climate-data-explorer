from __future__ import annotations

from agents.base_agent import Agent
from utils.helpers import safe_json_dumps


class AnomalyDetectorAgent(Agent):
    def __init__(self):
        super().__init__(
            name="AnomalyDetectorAgent",
            system_prompt=(
                "You are a climate anomaly detection agent. Explain unusual temperature, rainfall, "
                "or wind events using the supplied anomaly output. Highlight what stands out."
            ),
        )

    def build_user_message(self, context: dict) -> str:
        return (
            "Interpret the anomaly detection results for a climate dashboard.\n\n"
            f"{safe_json_dumps(context)}"
        )
