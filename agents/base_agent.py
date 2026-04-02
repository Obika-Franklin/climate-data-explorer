from __future__ import annotations

import json
from typing import Any, Callable, Dict

from tools.function_specs import TOOLS
from utils.azure_client import get_azure_client, get_deployment_name


class BaseAgent:
    def __init__(self, name: str, system_prompt: str, max_iterations: int = 3):
        self.name = name
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.client = get_azure_client()
        self.model = get_deployment_name()

    def run(
        self,
        user_prompt: str,
        tool_registry: Dict[str, Callable[..., Any]],
    ) -> dict:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        for _ in range(self.max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.2,
            )

            msg = response.choices[0].message

            if not getattr(msg, "tool_calls", None):
                return {
                    "agent": self.name,
                    "status": "success",
                    "content": msg.content,
                }

            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                }
            )

            for tc in msg.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments or "{}")

                if fn_name not in tool_registry:
                    tool_output = {"error": f"Unknown tool: {fn_name}"}
                else:
                    try:
                        tool_output = tool_registry[fn_name](**fn_args)
                    except Exception as e:
                        tool_output = {"error": str(e)}

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(tool_output, default=str),
                    }
                )

        return {
            "agent": self.name,
            "status": "failed",
            "content": "Max iterations reached before completion.",
        }
