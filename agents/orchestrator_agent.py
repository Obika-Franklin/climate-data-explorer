from agents.base_agent import BaseAgent


class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="OrchestratorAgent",
            system_prompt=(
                "You are the orchestration agent for a climate data explorer. "
                "Your job is to decide what information is needed from tools, then produce "
                "a structured handoff for specialist agents. "
                "Use tools when necessary. Be concise and structured."
            ),
        )
