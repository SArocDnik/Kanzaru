import json
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session
from sse_starlette.sse import EventSourceResponse
from src.api.deps import get_session
from src.config import settings
from src.models.db import Project, Chapter
from src.services.extractor import extract_from_text, extract_pdf_streaming

router = APIRouter(tags=["upload"])


@router.post("/projects/{project_id}/upload")
async def upload_to_project(
    project_id: int,
    session: Session = Depends(get_session),
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if file:
        upload_dir = settings.upload_path / Path(str(project_id))
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_name = Path(file.filename or "upload").name
        dest = upload_dir / safe_name

        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        chapter = Chapter(
            project_id=project_id,
            chapter_number=1,
            title=file.filename or "Uploaded file",
            file_path=str(dest),
            status="processing",
        )
        session.add(chapter)
        session.commit()
        session.refresh(chapter)

        return {
            "chapter_id": chapter.id,
            "file_path": str(dest),
            "status": "processing",
        }

    if text:
        full_text = text
        pages = extract_from_text(full_text)
        chapter = Chapter(
            project_id=project_id,
            chapter_number=1,
            title="Uploaded text",
            original_text=full_text,
            status="uploaded",
        )
        session.add(chapter)
        session.commit()
        session.refresh(chapter)
        return {"chapter_id": chapter.id, "pages": len(pages), "chars": len(full_text)}

    raise HTTPException(status_code=400, detail="No file or text provided")


@router.get("/chapters/{chapter_id}/extract/stream")
async def extract_stream(chapter_id: int, session: Session = Depends(get_session)):
    chapter = session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    if not chapter.file_path:
        raise HTTPException(status_code=400, detail="Chapter has no file to extract")

    file_path = chapter.file_path

    async def event_generator():
        full_text_parts: list[str] = []
        try:
            async for prog in extract_pdf_streaming(file_path):
                full_text_parts.append(prog.text)
                yield {
                    "event": "page",
                    "data": json.dumps({
                        "page": prog.page_num,
                        "total": prog.total_pages,
                        "method": prog.method,
                        "chars": prog.chars,
                    }),
                }
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}
            return

        full_text = "\n\n".join(t for t in full_text_parts if t)

        chapter.original_text = full_text
        chapter.status = "uploaded"
        session.add(chapter)
        session.commit()

        yield {
            "event": "done",
            "data": json.dumps({"chars": len(full_text), "pages": len(full_text_parts)}),
        }

    return EventSourceResponse(event_generator())
