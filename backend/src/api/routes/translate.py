import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from sse_starlette.sse import EventSourceResponse
from src.api.deps import get_session
from src.config import settings
from src.models.db import Chapter, Character, GlossaryEntry
from src.services.translator import TranslationContext, translate_chapter, translate_chapter_stream
from src.services.llm_client import LLMClient

router = APIRouter(tags=["translate"])


def _build_context(session: Session, chapter: Chapter) -> TranslationContext:
    chars = session.exec(
        select(Character).where(Character.project_id == chapter.project_id)
    ).all()
    char_str = "\n".join(f"- {c.name} ({c.role})" + (f" aliases: {c.aliases}" if c.aliases else "") for c in chars)

    glossary = session.exec(
        select(GlossaryEntry).where(GlossaryEntry.project_id == chapter.project_id)
    ).all()
    glossary_str = "\n".join(f"- {g.term} = {g.translation}" for g in glossary)

    return TranslationContext(
        summary=chapter.summary or "",
        characters=char_str or "",
        glossary=glossary_str or "",
    )


@router.post("/chapters/{chapter_id}/translate")
def translate_chapter_route(chapter_id: int, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if not chapter.original_text:
        raise HTTPException(status_code=400, detail="Chapter has no text to translate")

    ctx = _build_context(session, chapter)
    client = LLMClient(url=settings.ollama_url, model=settings.ollama_model)
    translated = translate_chapter(chapter.original_text, ctx, client)

    chapter.translated_text = translated
    chapter.status = "translated"
    session.add(chapter)
    session.commit()

    return {"chapter_id": chapter_id, "chars": len(translated)}


@router.get("/chapters/{chapter_id}/translation")
def get_translation(chapter_id: int, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return {"translated_text": chapter.translated_text, "status": chapter.status}


@router.put("/chapters/{chapter_id}/translation")
def update_translation(chapter_id: int, body: dict, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    chapter.translated_text = body.get("translated_text", "")
    session.add(chapter)
    session.commit()
    return {"chapter_id": chapter_id, "status": "updated"}


@router.get("/chapters/{chapter_id}/translate/stream")
async def translate_chapter_stream_route(chapter_id: int, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if not chapter.original_text:
        raise HTTPException(status_code=400, detail="Chapter has no text to translate")

    ctx = _build_context(session, chapter)
    client = LLMClient(url=settings.ollama_url, model=settings.ollama_model)

    async def event_generator():
        full_text = ""
        try:
            async for chunk in translate_chapter_stream(chapter.original_text, ctx, client):
                full_text += chunk
                yield {"event": "chunk", "data": json.dumps({"text": chunk})}
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
            return

        chapter.translated_text = full_text
        chapter.status = "translated"
        session.add(chapter)
        session.commit()
        yield {"event": "done", "data": json.dumps({"chars": len(full_text)})}

    return EventSourceResponse(event_generator())
