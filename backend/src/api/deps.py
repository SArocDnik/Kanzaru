from sqlmodel import Session, SQLModel, create_engine
from src.config import settings

engine = create_engine(settings.db_url, echo=False)


def init_db() -> None:
    import src.models.db  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
