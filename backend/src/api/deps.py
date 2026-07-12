from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import text
from src.config import settings

engine = create_engine(settings.db_url, echo=False)


def init_db() -> None:
    import src.models.db  # noqa: F401
    SQLModel.metadata.create_all(engine)
    _migrate(engine)


def _migrate(eng) -> None:
    with Session(eng) as session:
        cols = session.exec(text("PRAGMA table_info(chapter)")).all()
        col_names = {row[1] for row in cols}
        if col_names and "file_path" not in col_names:
            session.exec(text("ALTER TABLE chapter ADD COLUMN file_path TEXT DEFAULT ''"))
            session.commit()

        pcols = session.exec(text("PRAGMA table_info(project)")).all()
        pcol_names = {row[1] for row in pcols}
        if pcol_names:
            for col in ("genre", "sample_original", "sample_translated"):
                if col not in pcol_names:
                    session.exec(text(f"ALTER TABLE project ADD COLUMN {col} TEXT DEFAULT ''"))
                    session.commit()


def get_session() -> Session:
    with Session(engine) as session:
        yield session
