from unittest.mock import patch, MagicMock
import pytest
from src.services.llm_factory import get_llm_client
from src.services.llm_client import LLMClient
from src.services.gemini_client import GeminiClient


@patch("src.services.llm_factory.settings")
def test_factory_returns_gemini_client(mock_settings):
    mock_settings.llm_provider = "gemini"
    mock_settings.gemini_api_key = "test_key"
    mock_settings.gemini_model = "gemini-flash-latest"
    mock_settings.gemini_quality_model = "gemini-pro-latest"
    mock_settings.gemini_request_delay = 4.0
    mock_settings.gemini_max_retries = 3

    client = get_llm_client()
    assert isinstance(client, GeminiClient)
    assert client.model == "gemini-flash-latest"
    assert client.api_key == "test_key"


@patch("src.services.llm_factory.settings")
def test_factory_quality_uses_pro_model(mock_settings):
    mock_settings.llm_provider = "gemini"
    mock_settings.gemini_api_key = "test_key"
    mock_settings.gemini_model = "gemini-flash-latest"
    mock_settings.gemini_quality_model = "gemini-pro-latest"
    mock_settings.gemini_request_delay = 4.0
    mock_settings.gemini_max_retries = 3

    client = get_llm_client(quality=True)
    assert isinstance(client, GeminiClient)
    assert client.model == "gemini-pro-latest"


@patch("src.services.llm_factory.settings")
def test_factory_returns_ollama_client(mock_settings):
    mock_settings.llm_provider = "ollama"
    mock_settings.ollama_url = "http://localhost:11434"
    mock_settings.ollama_model = "qwen2.5:7b"

    client = get_llm_client()
    assert isinstance(client, LLMClient)
    assert client.url == "http://localhost:11434"
    assert client.model == "qwen2.5:7b"


@patch("src.services.llm_factory.settings")
def test_factory_ollama_ignores_quality(mock_settings):
    mock_settings.llm_provider = "ollama"
    mock_settings.ollama_url = "http://localhost:11434"
    mock_settings.ollama_model = "qwen2.5:7b"

    client = get_llm_client(quality=True)
    assert isinstance(client, LLMClient)
    assert client.model == "qwen2.5:7b"


@patch("src.services.llm_factory.settings")
def test_factory_gemini_no_key_raises(mock_settings):
    mock_settings.llm_provider = "gemini"
    mock_settings.gemini_api_key = ""

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY not set"):
        get_llm_client()
