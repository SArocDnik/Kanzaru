from dataclasses import dataclass
import re


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
