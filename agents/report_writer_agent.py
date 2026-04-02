from agents.base_agent import BaseAgent


class ReportWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ReportWriterAgent",
            system_prompt=(
                "You are a climate reporting agent. "
                "Combine specialist findings into a structured report with these sections: "
                "Dataset Summary, Trend Insights, Anomaly Insights, Final Interpretation. "
                "Write clearly for a non-technical audience."
            ),
        )
