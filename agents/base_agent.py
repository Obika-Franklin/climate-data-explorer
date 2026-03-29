from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from utils.azure_client import get_azure_client


@dataclass
class Agent:
    name: str
    system_prompt: str
    max_iterations: int = 3
    errors: list[str] = field(default_factory=list)

    def fallback(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "status": "fallback",
            "message": f"{self.name} could not use Azure OpenAI. Returning deterministic output instead.",
            "data": context,
        }

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        client, deployment = get_azure_client()
        if client is None or deployment is None:
            return self.fallback(context)

        last_error = None
        for _ in range(self.max_iterations):
            try:
                user_content = self.build_user_message(context)
                response = client.chat.completions.create(
                    model=deployment,
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                )
                content = response.choices[0].message.content or ""
                return {"agent": self.name, "status": "success", "content": content}
            except Exception as exc:  # pragma: no cover
                last_error = str(exc)
                self.errors.append(last_error)

        return {
            "agent": self.name,
            "status": "error",
            "message": f"{self.name} failed after {self.max_iterations} attempts.",
            "error": last_error,
        }

    def build_user_message(self, context: dict[str, Any]) -> str:
        raise NotImplementedError
