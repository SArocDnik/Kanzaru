from unittest.mock import MagicMock
import pytest
from src.services.translator import (
    TranslationContext, _chunk_text, build_prompt, translate_chapter, translate_chapter_stream
)


def test_chunk_text_short():
    assert _chunk_text("short text") == ["short text"]


def test_chunk_text_long():
    text = "line\n" * 2000  # ~10k chars
    chunks = _chunk_text(text, max_chars=1000)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 1000


def test_chunk_text_splits_on_newline():
    text = "A" * 900 + "\n" + "B" * 900
    chunks = _chunk_text(text, max_chars=1000)
    assert len(chunks) == 2
    assert chunks[0].startswith("A")
    assert chunks[1].startswith("B")


def test_build_prompt_includes_context():
    ctx = TranslationContext(summary="Hero's journey", characters="Taro (protagonist)", glossary="sensei=thầy")
    prompt = build_prompt("Some text", ctx)
    assert "Hero's journey" in prompt
    assert "Taro" in prompt
    assert "sensei=thầy" in prompt
    assert "Some text" in prompt
    assert "[cười]" in prompt


def test_translate_chapter_single_chunk():
    mock_client = MagicMock()
    mock_client.chat.return_value = "Xin chào"
    ctx = TranslationContext()
    result = translate_chapter("Hello", ctx, client=mock_client)
    assert result == "Xin chào"


def test_translate_chapter_multi_chunk():
    mock_client = MagicMock()
    mock_client.chat.side_effect = ["Phần 1", "Phần 2"]
    ctx = TranslationContext()
    long_text = "A" * 7000 + "\n" + "B" * 7000
    result = translate_chapter(long_text, ctx, client=mock_client)
    assert "Phần 1" in result
    assert "Phần 2" in result
    assert mock_client.chat.call_count == 2


@pytest.mark.asyncio
async def test_translate_stream_yields_chunks():
    mock_client = MagicMock()
    def fake_stream(messages):
        for word in ["Hello", " ", "world"]:
            yield word
    mock_client.stream.side_effect = lambda msgs: fake_stream(msgs)

    ctx = TranslationContext()
    chunks = []
    async for piece in translate_chapter_stream("Hello world", ctx, client=mock_client):
        chunks.append(piece)

    assert "".join(chunks).startswith("Hello")
