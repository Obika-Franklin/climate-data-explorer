from agents.base_agent import BaseAgent


class AnomalyDetectorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AnomalyDetectorAgent",
            system_prompt=(
                "You are a climate anomaly specialist. "
                "Use the anomaly tool to identify unusual observations and explain their significance. "
                "Discuss whether anomalies appear isolated, clustered, seasonal, or operationally meaningful."
            ),
        )
