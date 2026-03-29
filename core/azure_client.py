"""Azure OpenAI client helpers using the Azure OpenAI v1 API style."""

from __future__ import annotations

from typing import Optional

import streamlit as st
from openai import OpenAI


def azure_is_configured() -> bool:
    required = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT",
    ]
    return all(key in st.secrets for key in required)


def get_azure_client() -> Optional[OpenAI]:
    if not azure_is_configured():
        return None
    endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    return OpenAI(
        api_key=st.secrets["AZURE_OPENAI_API_KEY"],
        base_url=f"{endpoint}/openai/v1/",
    )


def get_deployment_name() -> Optional[str]:
    return st.secrets.get("AZURE_OPENAI_DEPLOYMENT") if azure_is_configured() else None
