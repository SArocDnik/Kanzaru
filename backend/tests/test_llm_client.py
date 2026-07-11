from unittest.mock import patch, MagicMock
import pytest
from src.services.llm_client import LLMClient


def test_llm_client_init():
    client = LLMClient(url="http://localhost:11434", model="qwen2.5:7b")
    assert client.url == "http://localhost:11434"
    assert client.model == "qwen2.5:7b"


@patch("src.services.llm_client.httpx.get")
def test_health_check_online(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"models": [{"name": "qwen2.5:7b"}, {"name": "llama3.1:8b"}]}
    mock_get.return_value = mock_resp

    client = LLMClient(url="http://localhost:11434", model="qwen2.5:7b")
    result = client.health_check()
    assert result["online"] is True
    assert result["model_available"] is True
    assert "qwen2.5:7b" in result["models"]


@patch("src.services.llm_client.httpx.get")
def test_health_check_offline(mock_get):
    mock_get.side_effect = Exception("Connection refused")

    client = LLMClient(url="http://localhost:99999", model="qwen2.5:7b")
    result = client.health_check()
    assert result["online"] is False
    assert result["model_available"] is False


@patch("src.services.llm_client.httpx.get")
def test_list_models(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"models": [{"name": "qwen2.5:7b"}, {"name": "llama3.1:8b"}]}
    mock_get.return_value = mock_resp

    client = LLMClient(url="http://localhost:11434", model="qwen2.5:7b")
    models = client.list_models()
    assert len(models) == 2
    assert "qwen2.5:7b" in models
    assert "llama3.1:8b" in models


@patch("src.services.llm_client.ollama")
def test_chat_returns_response(mock_ollama):
    mock_client = MagicMock()
    mock_ollama.Client.return_value = mock_client
    mock_resp = {"message": {"content": "Hello from LLM"}}
    mock_client.chat.return_value = mock_resp

    client = LLMClient(url="http://localhost:11434", model="qwen2.5:7b")
    result = client.chat([{"role": "user", "content": "Hi"}])
    assert result == "Hello from LLM"


@patch("src.services.llm_client.ollama")
def test_stream_yields_chunks(mock_ollama):
    mock_client = MagicMock()
    mock_ollama.Client.return_value = mock_client

    def fake_chat(*args, **kwargs):
        for chunk in [{"message": {"content": "Hello"}}, {"message": {"content": " world"}}]:
            yield chunk

    mock_client.chat.side_effect = lambda *a, **kw: fake_chat()

    client = LLMClient(url="http://localhost:11434", model="qwen2.5:7b")
    chunks = list(client.stream([{"role": "user", "content": "Hi"}]))
    assert chunks == ["Hello", " world"]
