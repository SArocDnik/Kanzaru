from dataclasses import dataclass
from typing import Optional, AsyncGenerator
from src.services.llm_client import LLMClient
from src.prompts.translate import TRANSLATE_PROMPT

MAX_CHUNK_CHARS = 8000


@dataclass
class TranslationContext:
    summary: str = ""
    characters: str = ""
    glossary: str = ""


def _chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    chunks = []
    remaining = text
    while len(remaining) > max_chars:
        split_at = remaining.rfind("\n", 0, max_chars)
        if split_at == -1:
            split_at = remaining.rfind(". ", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def build_prompt(text: str, ctx: TranslationContext) -> str:
    return TRANSLATE_PROMPT.format(
        summary=ctx.summary or "(no summary available)",
        characters=ctx.characters or "(no characters available)",
        glossary=ctx.glossary or "(no glossary)",
        text=text,
    )


def translate_chapter(
    text: str,
    ctx: TranslationContext,
    client: Optional[LLMClient] = None,
) -> str:
    if client is None:
        client = LLMClient()

    chunks = _chunk_text(text)
    results = []
    for chunk in chunks:
        prompt = build_prompt(chunk, ctx)
        messages = [{"role": "user", "content": prompt}]
        results.append(client.chat(messages))
    return "\n\n".join(results)


async def translate_chapter_stream(
    text: str,
    ctx: TranslationContext,
    client: Optional[LLMClient] = None,
) -> AsyncGenerator[str, None]:
    if client is None:
        client = LLMClient()

    chunks = _chunk_text(text)
    for i, chunk in enumerate(chunks):
        prompt = build_prompt(chunk, ctx)
        messages = [{"role": "user", "content": prompt}]
        for piece in client.stream(messages):
            yield piece
        if i < len(chunks) - 1:
            yield "\n\n"
