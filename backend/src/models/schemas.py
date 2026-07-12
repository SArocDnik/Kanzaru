from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class ProjectCreate(SQLModel):
    name: str
    source_lang: str = "auto"
    target_lang: str = "vi"
    genre: str = ""
    sample_original: str = ""
    sample_translated: str = ""


class ProjectRead(SQLModel):
    id: int
    name: str
    source_lang: str
    target_lang: str
    genre: str = ""
    sample_original: str = ""
    sample_translated: str = ""
    created_at: datetime
    updated_at: datetime


class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None
    genre: Optional[str] = None
    sample_original: Optional[str] = None
    sample_translated: Optional[str] = None


class ChapterCreate(SQLModel):
    chapter_number: int
    title: str = ""
    original_text: str = ""


class ChapterRead(SQLModel):
    id: int
    project_id: int
    chapter_number: int
    title: str
    original_text: str
    translated_text: str
    summary: str
    status: str
    file_path: str = ""


class ChapterUpdate(SQLModel):
    title: Optional[str] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    status: Optional[str] = None
