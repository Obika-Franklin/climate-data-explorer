from agents.base_agent import BaseAgent


class TrendAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TrendAnalystAgent",
            system_prompt=(
                "You are a climate trend analyst. "
                "Interpret seasonal patterns, rainfall behavior, temperature movement, "
                "wind behavior, and sunshine variation. "
                "Use tools when needed. Focus on natural-language reasoning, not raw code."
            ),
        )
