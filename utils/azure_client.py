from openai import AzureOpenAI
import streamlit as st


def get_azure_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=st.secrets["AZURE_OPENAI_API_KEY"],
        api_version=st.secrets["AZURE_OPENAI_API_VERSION"],
        azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
    )


def get_deployment_name() -> str:
    return st.secrets["AZURE_OPENAI_DEPLOYMENT"]


def azure_config_available() -> bool:
    required = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT",
    ]
    return all(k in st.secrets for k in required)
