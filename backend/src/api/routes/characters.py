from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from src.api.deps import get_session
from src.config import settings
from src.models.db import Character, CharacterRelationship, Chapter
from src.services.analyzer import CharacterInfo, map_relationships
from src.services.llm_factory import get_llm_client

router = APIRouter(tags=["characters"])


@router.get("/projects/{project_id}/characters")
def list_characters(project_id: int, session: Session = Depends(get_session)):
    chars = session.exec(
        select(Character).where(Character.project_id == project_id)
    ).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "aliases": c.aliases,
            "role": c.role,
            "honorifics": c.honorifics,
            "notes": c.notes,
        }
        for c in chars
    ]


@router.get("/projects/{project_id}/relationships")
def list_relationships(project_id: int, session: Session = Depends(get_session)):
    rels = session.exec(
        select(CharacterRelationship).where(CharacterRelationship.project_id == project_id)
    ).all()

    char_map = {}
    chars = session.exec(select(Character).where(Character.project_id == project_id)).all()
    for c in chars:
        char_map[c.id] = c.name

    nodes = [{"id": c.id, "name": c.name, "role": c.role} for c in chars]
    edges = [
        {
            "source": r.character_a_id,
            "target": r.character_b_id,
            "rel_type": r.rel_type,
            "description": r.description,
            "source_name": char_map.get(r.character_a_id, "?"),
            "target_name": char_map.get(r.character_b_id, "?"),
        }
        for r in rels
    ]
    return {"nodes": nodes, "edges": edges}


@router.post("/chapters/{chapter_id}/relationships")
def map_chapter_relationships(chapter_id: int, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    chars = session.exec(
        select(Character).where(Character.project_id == chapter.project_id)
    ).all()

    if not chars:
        raise HTTPException(status_code=400, detail="No characters found. Analyze chapter first.")

    char_infos = [
        CharacterInfo(name=c.name, role=c.role, aliases=c.aliases.split(",") if c.aliases else [])
        for c in chars
    ]

    client = get_llm_client(quality=False)
    relationships = map_relationships(char_infos, chapter.original_text, client)

    char_name_to_id = {c.name: c.id for c in chars}
    for c in chars:
        for alias in (c.aliases.split(",") if c.aliases else []):
            alias = alias.strip()
            if alias:
                char_name_to_id[alias] = c.id

    created = 0
    for rel in relationships:
        a_id = char_name_to_id.get(rel.character_a)
        b_id = char_name_to_id.get(rel.character_b)
        if not a_id or not b_id or a_id == b_id:
            continue

        existing = session.exec(
            select(CharacterRelationship).where(
                CharacterRelationship.project_id == chapter.project_id,
                CharacterRelationship.character_a_id == a_id,
                CharacterRelationship.character_b_id == b_id,
            )
        ).first()
        if existing:
            continue

        rel_obj = CharacterRelationship(
            project_id=chapter.project_id,
            character_a_id=a_id,
            character_b_id=b_id,
            rel_type=rel.rel_type,
            description=rel.description,
        )
        session.add(rel_obj)
        created += 1

    session.commit()
    return {"relationships_created": created, "total": len(relationships)}
