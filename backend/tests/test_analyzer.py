from unittest.mock import patch, MagicMock
import pytest
from src.services.analyzer import analyze_chapter, AnalysisResult, CharacterInfo, _parse_llm_json


MOCK_LLM_RESPONSE = """{
  "summary": "A young hero meets a mysterious mentor.",
  "characters": [
    {"name": "Taro", "aliases": ["Tarou"], "role": "protagonist", "honorifics_used": ["kun"]},
    {"name": "Sora", "aliases": [], "role": "supporting", "honorifics_used": ["san", "sama"]}
  ],
  "key_terms": [
    {"term": "ki", "meaning": "energy"}
  ]
}"""


def test_parse_llm_json_plain():
    data = _parse_llm_json('{"key": "value"}')
    assert data["key"] == "value"


def test_parse_llm_json_markdown_wrapped():
    data = _parse_llm_json('```json\n{"key": "value"}\n```')
    assert data["key"] == "value"


def test_analyze_chapter_success():
    mock_client = MagicMock()
    mock_client.chat.return_value = MOCK_LLM_RESPONSE

    result = analyze_chapter("Some chapter text", client=mock_client)

    assert isinstance(result, AnalysisResult)
    assert "young hero" in result.summary
    assert len(result.characters) == 2
    assert result.characters[0].name == "Taro"
    assert result.characters[0].role == "protagonist"
    assert "kun" in result.characters[0].honorifics_used
    assert result.characters[1].name == "Sora"
    assert len(result.key_terms) == 1
    assert result.key_terms[0].term == "ki"


def test_analyze_chapter_invalid_json_fallback():
    mock_client = MagicMock()
    mock_client.chat.return_value = "This is not JSON at all."

    result = analyze_chapter("text", client=mock_client)
    assert result.summary == "This is not JSON at all."
    assert len(result.characters) == 0


def test_analyze_chapter_empty_response():
    mock_client = MagicMock()
    mock_client.chat.return_value = "{}"

    result = analyze_chapter("text", client=mock_client)
    assert result.summary == ""
    assert len(result.characters) == 0


def test_analyze_chapter_truncates_long_text():
    mock_client = MagicMock()
    mock_client.chat.return_value = MOCK_LLM_RESPONSE

    long_text = "A" * 10000
    analyze_chapter(long_text, client=mock_client)

    sent_content = mock_client.chat.call_args[0][0][0]["content"]
    assert len(sent_content) < 10000
