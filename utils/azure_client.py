from __future__ import annotations

import streamlit as st
from openai import AzureOpenAI


REQUIRED_SECRETS = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_DEPLOYMENT",
    "AZURE_OPENAI_API_VERSION",
]


def azure_config_available() -> bool:
    return all(key in st.secrets for key in REQUIRED_SECRETS)


def get_azure_client() -> tuple[AzureOpenAI | None, str | None]:
    if not azure_config_available():
        return None, None

    client = AzureOpenAI(
        api_key=st.secrets["AZURE_OPENAI_API_KEY"],
        api_version=st.secrets["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
    )
    return client, st.secrets["AZURE_OPENAI_DEPLOYMENT"]
