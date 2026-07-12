from dataclasses import dataclass
from typing import Optional, AsyncGenerator
from src.services.llm_client import LLMClient
from src.prompts.translate import TRANSLATE_PROMPT, ROUGH_PROMPT, CRITIQUE_PROMPT, FINAL_PROMPT

MAX_CHUNK_CHARS = 8000


@dataclass
class TranslationContext:
    summary: str = ""
    characters: str = ""
    glossary: str = ""
    relationships: str = ""
    genre: str = "fiction"
    source_lang: str = "auto"
    sample_original: str = ""
    sample_translated: str = ""


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
    sample_section = ""
    if ctx.sample_original and ctx.sample_translated:
        sample_section = (
            f"\nVăn bản mẫu:\n{ctx.sample_original}\n→ {ctx.sample_translated}\n"
            "Hãy dịch theo phong cách tương tự.\n"
        )
    return TRANSLATE_PROMPT.format(
        source_lang=ctx.source_lang or "ngôn ngữ gốc",
        genre=ctx.genre or "fiction",
        summary=ctx.summary or "(không có tóm tắt)",
        characters=ctx.characters or "(không có thông tin nhân vật)",
        relationships=ctx.relationships or "(không có quan hệ nhân vật)",
        glossary=ctx.glossary or "(không có glossary)",
        sample_section=sample_section,
        text=text,
    )


def build_3step_prompts(text: str, ctx: TranslationContext) -> list[str]:
    base = build_prompt(text, ctx)
    rough = ROUGH_PROMPT.format(base_prompt=base)
    critique = CRITIQUE_PROMPT.format(text=text, rough_translation="(sẽ được điền sau)")
    final = FINAL_PROMPT.format(text=text, rough_translation="(sẽ được điền sau)", critique="(sẽ được điền sau)")
    return [rough, critique, final]


def translate_chapter_3step(
    text: str,
    ctx: TranslationContext,
    client: Optional[LLMClient] = None,
) -> str:
    if client is None:
        client = LLMClient()

    chunks = _chunk_text(text)
    results = []
    for chunk in chunks:
        base = build_prompt(chunk, ctx)
        rough_prompt = ROUGH_PROMPT.format(base_prompt=base)

        rough = client.chat([{"role": "user", "content": rough_prompt}])

        critique_prompt = CRITIQUE_PROMPT.format(text=chunk, rough_translation=rough)
        critique = client.chat([
            {"role": "user", "content": rough_prompt},
            {"role": "assistant", "content": rough},
            {"role": "user", "content": critique_prompt},
        ])

        final_prompt = FINAL_PROMPT.format(
            text=chunk,
            rough_translation=rough,
            critique=critique,
        )
        final = client.chat([
            {"role": "user", "content": rough_prompt},
            {"role": "assistant", "content": rough},
            {"role": "user", "content": critique_prompt},
            {"role": "assistant", "content": critique},
            {"role": "user", "content": final_prompt},
        ])
        results.append(final)
    return "\n\n".join(results)


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
