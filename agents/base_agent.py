"""Base Agent class."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from core.safety import MAX_ITERATIONS
from core.tools import TOOL_DEFINITIONS, execute_tool


class Agent:
    def __init__(self, name: str, system_prompt: str, client=None, deployment_name: str | None = None, max_iterations: int = MAX_ITERATIONS):
        self.name = name
        self.system_prompt = system_prompt
        self.client = client
        self.deployment_name = deployment_name
        self.max_iterations = max_iterations

    def heuristic(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def run(self, df: pd.DataFrame, user_question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        if self.client is None or self.deployment_name is None:
            return self.heuristic(df, context)

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": (
                    f"User question: {user_question}\n\n"
                    f"Context: {context}\n\n"
                    "Use tools where needed, then return JSON with keys: summary, bullets, risks, recommendations."
                ),
            },
        ]

        for _ in range(self.max_iterations):
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=0.2,
            )
            message = response.choices[0].message

            if getattr(message, "tool_calls", None):
                messages.append(message.model_dump())
                for tool_call in message.tool_calls:
                    result = execute_tool(tool_call.function.name, tool_call.function.arguments, df)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": result,
                        }
                    )
                continue

            content = message.content or "{}"
            return {
                "status": "ok",
                "agent": self.name,
                "raw": content,
            }

        return {
            "status": "error",
            "agent": self.name,
            "raw": "Max iterations reached before final answer.",
        }
