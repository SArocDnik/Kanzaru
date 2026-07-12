from unittest.mock import MagicMock
import json
import pytest
from src.services.chapter_splitter import (
    detect_chapters,
    detect_chapters_llm,
    detect_chapters_with_fallback,
    ChapterResult,
)


MOCK_LLM_RESPONSE = json.dumps({
    "chapters": [
        {"title": "Prologue: The Beginning", "start_marker": "The dawn broke over the silent city.", "estimated_number": 1},
        {"title": "Chapter 1: A New World", "start_marker": "Chapter 1: A New World\nThe morning came swiftly.", "estimated_number": 2},
        {"title": "Epilogue", "start_marker": "Years later, the city had changed.", "estimated_number": 3},
    ]
})


def test_detect_chapters_llm_parses_response():
    mock_client = MagicMock()
    mock_client.chat.return_value = MOCK_LLM_RESPONSE

    text = (
        "The dawn broke over the silent city. It was a quiet morning.\n\n"
        "Chapter 1: A New World\nThe morning came swiftly. Taro woke up.\n\n"
        "Years later, the city had changed. The end."
    )

    chapters = detect_chapters_llm(text, mock_client)
    assert len(chapters) == 3
    assert "Prologue" in chapters[0].title
    assert "Chapter 1" in chapters[1].title
    assert "Epilogue" in chapters[2].title
    assert "silent city" in chapters[0].content
    assert "Taro woke up" in chapters[1].content
    assert "The end" in chapters[2].content


def test_detect_chapters_llm_invalid_json_returns_single():
    mock_client = MagicMock()
    mock_client.chat.return_value = "not json at all"

    text = "Some text without clear structure."
    chapters = detect_chapters_llm(text, mock_client)
    assert len(chapters) == 1
    assert chapters[0].title == "Chapter 1"


def test_detect_chapters_llm_empty_chapters_returns_single():
    mock_client = MagicMock()
    mock_client.chat.return_value = json.dumps({"chapters": []})

    text = "Some text."
    chapters = detect_chapters_llm(text, mock_client)
    assert len(chapters) == 1


def test_detect_chapters_llm_marker_not_found_skips():
    mock_client = MagicMock()
    mock_client.chat.return_value = json.dumps({
        "chapters": [
            {"title": "Chapter 1", "start_marker": "NONEXISTENT MARKER XYZ", "estimated_number": 1},
            {"title": "Chapter 2", "start_marker": "Also nonexistent", "estimated_number": 2},
        ]
    })

    text = "Some text without matching markers."
    chapters = detect_chapters_llm(text, mock_client)
    assert len(chapters) == 1
    assert chapters[0].title == "Chapter 1"


def test_detect_chapters_with_fallback_uses_regex_first():
    text = "Chương 1\nNội dung 1\n\nChương 2\nNội dung 2"
    mock_client = MagicMock()
    chapters = detect_chapters_with_fallback(text, client=mock_client)
    assert len(chapters) == 2
    assert chapters[0].title == "Chương 1"
    mock_client.chat.assert_not_called()


def test_detect_chapters_with_fallback_uses_llm_when_regex_fails():
    mock_client = MagicMock()
    mock_client.chat.return_value = MOCK_LLM_RESPONSE

    text = (
        "The dawn broke over the silent city. It was a quiet morning.\n\n"
        "Chapter 1: A New World\nThe morning came swiftly. Taro woke up.\n\n"
        "Years later, the city had changed. The end."
    )
    chapters = detect_chapters_with_fallback(text, client=mock_client)
    assert len(chapters) == 3
    mock_client.chat.assert_called_once()


def test_detect_chapters_with_fallback_no_client_returns_regex():
    text = "No chapter markers here. Just continuous text."
    chapters = detect_chapters_with_fallback(text, client=None)
    assert len(chapters) == 1
    assert chapters[0].title == "Chapter 1"
