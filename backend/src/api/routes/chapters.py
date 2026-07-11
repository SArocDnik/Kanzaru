from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from src.api.deps import get_session
from src.config import settings
from src.models.db import Project, Chapter, Character
from src.models.schemas import ChapterCreate, ChapterRead, ChapterUpdate
from src.services.chapter_splitter import detect_chapters
from src.services.analyzer import analyze_chapter
from src.services.llm_client import LLMClient

router = APIRouter(tags=["chapters"])


@router.post("/projects/{project_id}/chapters", response_model=ChapterRead, status_code=status.HTTP_201_CREATED)
def create_chapter(project_id: int, data: ChapterCreate, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    chapter = Chapter(project_id=project_id, **data.model_dump())
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    return chapter


@router.post("/projects/{project_id}/chapters/detect", response_model=list[ChapterRead], status_code=status.HTTP_201_CREATED)
def detect_chapters_route(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    existing = session.exec(
        select(Chapter).where(Chapter.project_id == project_id)
    ).all()

    source_text = ""
    for ch in existing:
        if ch.original_text:
            source_text = ch.original_text
            break

    if not source_text:
        raise HTTPException(status_code=400, detail="No text to detect chapters from. Upload text first.")

    for ch in existing:
        session.delete(ch)
    session.commit()

    detected = detect_chapters(source_text, project.source_lang)

    created = []
    for i, ch in enumerate(detected):
        chapter = Chapter(
            project_id=project_id,
            chapter_number=i + 1,
            title=ch.title,
            original_text=ch.content,
            status="detected",
        )
        session.add(chapter)
        created.append(chapter)

    session.commit()
    for ch in created:
        session.refresh(ch)
    return created


@router.get("/projects/{project_id}/chapters", response_model=list[ChapterRead])
def list_chapters(project_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Chapter).where(Chapter.project_id == project_id).order_by(Chapter.chapter_number)).all()


@router.get("/chapters/{chapter_id}", response_model=ChapterRead)
def get_chapter(chapter_id: int, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.put("/chapters/{chapter_id}", response_model=ChapterRead)
def update_chapter(chapter_id: int, data: ChapterUpdate, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(chapter, k, v)
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    return chapter


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter(chapter_id: int, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    session.delete(chapter)
    session.commit()


@router.post("/chapters/{chapter_id}/analyze")
def analyze_chapter_route(chapter_id: int, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if not chapter.original_text:
        raise HTTPException(status_code=400, detail="Chapter has no text to analyze")

    project = session.get(Project, chapter.project_id)

    client = LLMClient(url=settings.ollama_url, model=settings.ollama_model)
    result = analyze_chapter(chapter.original_text, project.source_lang if project else "auto", client)

    chapter.summary = result.summary
    chapter.status = "analyzed"
    chapter.analysis_json = result.summary
    session.add(chapter)

    for ch_info in result.characters:
        existing = session.exec(
            select(Character).where(
                Character.project_id == chapter.project_id,
                Character.name == ch_info.name,
            )
        ).first()
        if existing:
            if ch_info.aliases:
                existing.aliases = ",".join(ch_info.aliases)
            if ch_info.role:
                existing.role = ch_info.role
            if ch_info.honorifics_used:
                existing.honorifics = ",".join(ch_info.honorifics_used)
            session.add(existing)
        else:
            char = Character(
                project_id=chapter.project_id,
                name=ch_info.name,
                aliases=",".join(ch_info.aliases),
                role=ch_info.role,
                honorifics=",".join(ch_info.honorifics_used),
                first_chapter_id=chapter_id,
            )
            session.add(char)

    session.commit()
    return {"summary": result.summary, "characters": len(result.characters), "key_terms": len(result.key_terms)}


@router.get("/chapters/{chapter_id}/analysis")
def get_analysis(chapter_id: int, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    characters = session.exec(
        select(Character).where(Character.project_id == chapter.project_id)
    ).all()
    return {
        "summary": chapter.summary,
        "status": chapter.status,
        "characters": [
            {"name": c.name, "aliases": c.aliases, "role": c.role, "honorifics": c.honorifics}
            for c in characters
        ],
    }
