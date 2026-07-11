from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session
from src.api.deps import get_session
from src.models.db import Project, Chapter
from src.services.extractor import extract_from_text, extract_from_pdf

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
        content = await file.read()
        if file.filename and file.filename.lower().endswith(".pdf"):
            pages = extract_from_pdf(content)
            full_text = "\n\n".join(p.text for p in pages if p.text)
        else:
            full_text = content.decode("utf-8", errors="replace")
            pages = extract_from_text(full_text)
    elif text:
        full_text = text
        pages = extract_from_text(full_text)
    else:
        raise HTTPException(status_code=400, detail="No file or text provided")

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
