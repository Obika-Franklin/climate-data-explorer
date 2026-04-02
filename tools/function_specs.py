TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_climate_summary",
            "description": "Return a structured summary of the currently filtered Heathrow climate dataset.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_anomalies",
            "description": "Detect unusual climate observations using a z-score threshold.",
            "parameters": {
                "type": "object",
                "properties": {
                    "z_threshold": {
                        "type": "number",
                        "description": "Z-score threshold for anomaly detection, e.g. 2.0"
                    }
                },
                "required": ["z_threshold"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_monthly_trends",
            "description": "Return monthly aggregated trends for temperature, rainfall, wind speed, pressure, and sunshine.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
    },
]
