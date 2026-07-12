from dataclasses import dataclass
import json
import re
from typing import Optional

from src.services.llm_provider import LLMProvider


@dataclass
class ChapterResult:
    title: str
    content: str


PATTERNS = [
    r"(?:^|\n)(Chương\s+\d+)[^\n]*",
    r"(?:^|\n)(第.+?章)[^\n]*",
    r"(?:^|\n)(Chapter\s+\d+)[^\n]*",
    r"(?:^|\n)(第.+?話)[^\n]*",
    r"(?:^|\n)(第.+?回)[^\n]*",
]

COMBINED = re.compile("|".join(f"(?:{p})" for p in PATTERNS))


def detect_chapters(text: str, lang_hint: str = "") -> list[ChapterResult]:
    matches = list(COMBINED.finditer(text))

    if not matches:
        return [ChapterResult(title="Chapter 1", content=text.strip())]

    chapters: list[ChapterResult] = []

    for i, m in enumerate(matches):
        full_match = m.group(0).strip()
        title = full_match.lstrip("\n").strip()

        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()

        chapters.append(ChapterResult(title=title, content=content))

    return chapters


def _parse_llm_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    return json.loads(text)


def detect_chapters_llm(
    text: str,
    client: LLMProvider,
    max_chars: int = 30000,
) -> list[ChapterResult]:
    from src.prompts.chapter_detect import CHAPTER_DETECT_PROMPT

    truncated = text[:max_chars] if len(text) > max_chars else text
    prompt = CHAPTER_DETECT_PROMPT.format(max_chars=max_chars, text=truncated)
    raw = client.chat([{"role": "user", "content": prompt}])

    try:
        data = _parse_llm_json(raw)
    except (json.JSONDecodeError, ValueError):
        return [ChapterResult(title="Chapter 1", content=text.strip())]

    chapter_defs = data.get("chapters", [])
    if not chapter_defs:
        return [ChapterResult(title="Chapter 1", content=text.strip())]

    chapters: list[ChapterResult] = []
    for i, ch in enumerate(chapter_defs):
        title = ch.get("title", f"Chapter {i + 1}")
        marker = ch.get("start_marker", "")

        start_idx = text.find(marker) if marker else -1
        if start_idx == -1:
            marker_short = marker[:40] if len(marker) > 40 else marker
            start_idx = text.find(marker_short) if marker_short else -1

        if start_idx == -1:
            if i == 0:
                start_idx = 0
            else:
                continue

        end_idx = len(text)
        for j in range(i + 1, len(chapter_defs)):
            next_marker = chapter_defs[j].get("start_marker", "")
            if next_marker:
                next_idx = text.find(next_marker, start_idx + 1)
                if next_idx == -1 and len(next_marker) > 40:
                    next_idx = text.find(next_marker[:40], start_idx + 1)
                if next_idx != -1:
                    end_idx = next_idx
                    break

        content = text[start_idx:end_idx].strip()
        if content:
            chapters.append(ChapterResult(title=title, content=content))

    if not chapters:
        chapters = [ChapterResult(title="Chapter 1", content=text.strip())]

    return chapters


def detect_chapters_with_fallback(
    text: str,
    client: Optional[LLMProvider] = None,
    lang_hint: str = "",
) -> list[ChapterResult]:
    regex_result = detect_chapters(text, lang_hint)
    if len(regex_result) > 1:
        return regex_result

    if client is None:
        return regex_result

    return detect_chapters_llm(text, client)

