from unittest.mock import patch, MagicMock
import json
import pytest
from src.services.gemini_client import GeminiClient


def _mock_response(text: str, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": text}]}}]
    }
    resp.text = json.dumps(resp.json.return_value)
    resp.raise_for_status = MagicMock()
    return resp


def test_gemini_client_init():
    client = GeminiClient(api_key="test_key", model="gemini-2.5-flash")
    assert client.api_key == "test_key"
    assert client.model == "gemini-2.5-flash"
    assert client.request_delay == 4.0
    assert client.max_retries == 3


def test_gemini_client_implements_protocol():
    from src.services.llm_provider import LLMProvider
    client = GeminiClient(api_key="test_key")
    assert isinstance(client, LLMProvider)


@patch("src.services.gemini_client.httpx.post")
def test_chat_returns_text(mock_post):
    mock_post.return_value = _mock_response("Xin chào")
    client = GeminiClient(api_key="test_key", request_delay=0)
    result = client.chat([{"role": "user", "content": "Hello"}])
    assert result == "Xin chào"
    args, kwargs = mock_post.call_args
    assert "X-goog-api-key" in kwargs["headers"]
    assert kwargs["headers"]["X-goog-api-key"] == "test_key"
    body = kwargs["json"]
    assert body["contents"][0]["role"] == "user"
    assert body["contents"][0]["parts"][0]["text"] == "Hello"


@patch("src.services.gemini_client.httpx.post")
def test_chat_maps_assistant_role_to_model(mock_post):
    mock_post.return_value = _mock_response("OK")
    client = GeminiClient(api_key="test_key", request_delay=0)
    client.chat([
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello"},
        {"role": "user", "content": "Bye"},
    ])
    body = mock_post.call_args.kwargs["json"]
    assert body["contents"][0]["role"] == "user"
    assert body["contents"][1]["role"] == "model"
    assert body["contents"][2]["role"] == "user"


@patch("src.services.gemini_client.httpx.post")
def test_chat_includes_safety_settings(mock_post):
    mock_post.return_value = _mock_response("OK")
    client = GeminiClient(api_key="test_key", request_delay=0)
    client.chat([{"role": "user", "content": "Hi"}])
    body = mock_post.call_args.kwargs["json"]
    assert "safetySettings" in body
    assert len(body["safetySettings"]) == 4
    assert all(s["threshold"] == "BLOCK_NONE" for s in body["safetySettings"])


@patch("src.services.gemini_client.httpx.post")
def test_chat_retries_on_429(mock_post):
    rate_limit_resp = MagicMock()
    rate_limit_resp.status_code = 429
    rate_limit_resp.text = "rate limited"

    mock_post.side_effect = [rate_limit_resp, _mock_response("Success after retry")]
    client = GeminiClient(api_key="test_key", request_delay=0, max_retries=3)
    result = client.chat([{"role": "user", "content": "Hi"}])
    assert result == "Success after retry"
    assert mock_post.call_count == 2


@patch("src.services.gemini_client.httpx.post")
def test_chat_raises_on_401_no_retry(mock_post):
    err_resp = MagicMock()
    err_resp.status_code = 401
    err_resp.text = "invalid key"
    mock_post.return_value = err_resp

    client = GeminiClient(api_key="bad_key", request_delay=0, max_retries=3)
    with pytest.raises(RuntimeError, match="auth/error"):
        client.chat([{"role": "user", "content": "Hi"}])
    assert mock_post.call_count == 1


@patch("src.services.gemini_client.httpx.post")
def test_chat_raises_after_max_retries(mock_post):
    rate_limit_resp = MagicMock()
    rate_limit_resp.status_code = 429
    rate_limit_resp.text = "rate limited"
    mock_post.return_value = rate_limit_resp

    client = GeminiClient(api_key="test_key", request_delay=0, max_retries=2)
    with pytest.raises(RuntimeError, match="rate limit"):
        client.chat([{"role": "user", "content": "Hi"}])
    assert mock_post.call_count == 3


@patch("src.services.gemini_client.httpx.post")
def test_chat_raises_on_no_candidates(mock_post):
    empty_resp = MagicMock()
    empty_resp.status_code = 200
    empty_resp.json.return_value = {"candidates": []}
    empty_resp.text = "{}"
    empty_resp.raise_for_status = MagicMock()
    mock_post.return_value = empty_resp

    client = GeminiClient(api_key="test_key", request_delay=0)
    with pytest.raises(RuntimeError, match="no candidates"):
        client.chat([{"role": "user", "content": "Hi"}])


@patch("src.services.gemini_client.httpx.stream")
def test_stream_yields_chunks(mock_stream):
    chunks = [
        {"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]},
        {"candidates": [{"content": {"parts": [{"text": " world"}]}}]},
    ]
    sse_lines = []
    for c in chunks:
        sse_lines.append("data: " + json.dumps(c))
    sse_lines.append("data: [DONE]")

    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_ctx.status_code = 200
    mock_ctx.raise_for_status = MagicMock()
    mock_ctx.iter_lines = MagicMock(return_value=iter(sse_lines))
    mock_stream.return_value = mock_ctx

    client = GeminiClient(api_key="test_key", request_delay=0)
    result = list(client.stream([{"role": "user", "content": "Hi"}]))
    assert result == ["Hello", " world"]


@patch("src.services.gemini_client.httpx.get")
def test_health_check_online(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp

    client = GeminiClient(api_key="test_key", model="gemini-2.5-flash")
    result = client.health_check()
    assert result["online"] is True
    assert result["provider"] == "gemini"
    assert result["model"] == "gemini-2.5-flash"
    assert result["model_available"] is True


def test_health_check_no_key():
    client = GeminiClient(api_key="", model="gemini-2.5-flash")
    result = client.health_check()
    assert result["online"] is False
    assert "API key not set" in result["error"]


@patch("src.services.gemini_client.httpx.get")
def test_list_models(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "models": [
            {"name": "models/gemini-2.5-flash"},
            {"name": "models/gemini-2.5-pro"},
        ]
    }
    mock_get.return_value = mock_resp

    client = GeminiClient(api_key="test_key")
    models = client.list_models()
    assert "gemini-2.5-flash" in models
    assert "gemini-2.5-pro" in models
