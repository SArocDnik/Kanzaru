import pytest
from sqlmodel import create_engine, Session, text
from sqlalchemy.pool import StaticPool

from src.api.deps import init_db


def test_init_db_adds_file_path_column_to_existing_chapter_table():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    with Session(eng) as session:
        session.exec(text("""
            CREATE TABLE project (
                id INTEGER PRIMARY KEY,
                name TEXT,
                source_lang TEXT,
                target_lang TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        """))
        session.exec(text("""
            CREATE TABLE chapter (
                id INTEGER PRIMARY KEY,
                project_id INTEGER,
                chapter_number INTEGER,
                title TEXT,
                original_text TEXT,
                translated_text TEXT,
                summary TEXT,
                analysis_json TEXT,
                status TEXT,
                FOREIGN KEY (project_id) REFERENCES project (id)
            )
        """))
        session.commit()

    original_engine = None
    import src.api.deps as deps
    original_engine = deps.engine
    deps.engine = eng
    try:
        init_db()
    finally:
        deps.engine = original_engine

    with Session(eng) as session:
        cols = session.exec(text("PRAGMA table_info(chapter)")).all()
        col_names = [row[1] for row in cols]
        assert "file_path" in col_names

        session.exec(text("""
            INSERT INTO chapter (project_id, chapter_number, title, original_text,
                                 translated_text, summary, analysis_json, file_path, status)
            VALUES (1, 1, 'test', 'text', '', '', '', 'uploads/test.pdf', 'processing')
        """))
        session.commit()

    with Session(eng) as session:
        pcols = session.exec(text("PRAGMA table_info(project)")).all()
        pcol_names = [row[1] for row in pcols]
        assert "genre" in pcol_names
        assert "sample_original" in pcol_names
        assert "sample_translated" in pcol_names
