from __future__ import annotations

import json
from datetime import datetime
from typing import Any


def safe_json_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, default=str)


def format_date(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    try:
        return str(value)[:10]
    except Exception:
        return "N/A"
