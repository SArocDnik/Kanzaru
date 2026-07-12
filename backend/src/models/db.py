from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    source_lang: str = "auto"
    target_lang: str = "vi"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    chapters: list["Chapter"] = Relationship(back_populates="project", cascade_delete=True)
    glossary: list["GlossaryEntry"] = Relationship(back_populates="project", cascade_delete=True)
    characters: list["Character"] = Relationship(back_populates="project", cascade_delete=True)


class Chapter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    chapter_number: int
    title: str = ""
    original_text: str = ""
    translated_text: str = ""
    summary: str = ""
    analysis_json: str = ""
    file_path: str = ""
    status: str = "pending"

    project: Optional[Project] = Relationship(back_populates="chapters")
    audio_files: list["AudioFile"] = Relationship(back_populates="chapter", cascade_delete=True)


class Character(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    name: str
    aliases: str = ""
    role: str = ""
    honorifics: str = ""
    notes: str = ""
    first_chapter_id: Optional[int] = Field(default=None, foreign_key="chapter.id")

    project: Optional[Project] = Relationship(back_populates="characters")


class CharacterRelationship(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    character_a_id: int = Field(foreign_key="character.id")
    character_b_id: int = Field(foreign_key="character.id")
    rel_type: str
    description: str = ""


class GlossaryEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    term: str
    translation: str
    source_lang: str = ""
    notes: str = ""

    project: Optional[Project] = Relationship(back_populates="glossary")


class AudioFile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chapter_id: int = Field(foreign_key="chapter.id")
    voice: str
    style: str = "doc_truyen"
    file_path_wav: str = ""
    file_path_mp3: str = ""
    duration_sec: float = 0.0
    segment_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    chapter: Optional[Chapter] = Relationship(back_populates="audio_files")
    timeline: list["AudioTimeline"] = Relationship(back_populates="audio_file", cascade_delete=True)


class AudioTimeline(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    audio_file_id: int = Field(foreign_key="audiofile.id")
    segment_index: int
    text: str
    start_time: float = 0.0
    end_time: float = 0.0

    audio_file: Optional[AudioFile] = Relationship(back_populates="timeline")
