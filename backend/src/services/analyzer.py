import json
from dataclasses import dataclass, field
from typing import Optional
from src.services.llm_client import LLMClient
from src.prompts.analyze import ANALYZE_PROMPT, RELATIONSHIP_PROMPT


@dataclass
class CharacterInfo:
    name: str
    aliases: list[str] = field(default_factory=list)
    role: str = ""
    honorifics_used: list[str] = field(default_factory=list)


@dataclass
class KeyTerm:
    term: str
    meaning: str = ""


@dataclass
class Relationship:
    character_a: str
    character_b: str
    rel_type: str
    description: str = ""


@dataclass
class AnalysisResult:
    summary: str = ""
    characters: list[CharacterInfo] = field(default_factory=list)
    key_terms: list[KeyTerm] = field(default_factory=list)


def _parse_llm_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    return json.loads(text)


def analyze_chapter(text: str, lang: str = "auto", client: Optional[LLMClient] = None) -> AnalysisResult:
    if client is None:
        client = LLMClient()

    prompt = ANALYZE_PROMPT.format(text=text[:4000])
    messages = [{"role": "user", "content": prompt}]
    raw = client.chat(messages)

    try:
        data = _parse_llm_json(raw)
    except (json.JSONDecodeError, ValueError):
        return AnalysisResult(summary=raw[:500])

    result = AnalysisResult(summary=data.get("summary", ""))

    for ch in data.get("characters", []):
        result.characters.append(CharacterInfo(
            name=ch.get("name", ""),
            aliases=ch.get("aliases", []),
            role=ch.get("role", ""),
            honorifics_used=ch.get("honorifics_used", []),
        ))

    for kt in data.get("key_terms", []):
        result.key_terms.append(KeyTerm(
            term=kt.get("term", ""),
            meaning=kt.get("meaning", ""),
        ))

    return result


def map_relationships(
    characters: list[CharacterInfo],
    chapter_text: str,
    client: Optional[LLMClient] = None,
) -> list[Relationship]:
    if not characters or not chapter_text:
        return []
    if client is None:
        client = LLMClient()

    char_list = "\n".join(f"- {c.name} ({c.role})" for c in characters)
    prompt = RELATIONSHIP_PROMPT.format(characters=char_list, text=chapter_text[:4000])
    messages = [{"role": "user", "content": prompt}]
    raw = client.chat(messages)

    try:
        data = _parse_llm_json(raw)
    except (json.JSONDecodeError, ValueError):
        return []

    relationships = []
    for rel in data.get("relationships", []):
        relationships.append(Relationship(
            character_a=rel.get("character_a", ""),
            character_b=rel.get("character_b", ""),
            rel_type=rel.get("rel_type", "other"),
            description=rel.get("description", ""),
        ))

    return relationships
