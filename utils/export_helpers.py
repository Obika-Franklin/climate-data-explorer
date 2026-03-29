"""Export helpers for JSON and report text."""

from __future__ import annotations

import json
from typing import Any, Dict


def to_pretty_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, default=str)
