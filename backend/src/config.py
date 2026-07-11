from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    db_path: str = "data/kanzaru.db"
    audio_dir: str = "audio"
    tts_voice: str = "Phạm Tuyên"
    tts_style: str = "doc_truyen"
    tts_precision: str = "int8"
    upload_dir: str = "uploads"
    cors_origins: str = "http://localhost:5173"

    model_config = {"env_prefix": "KANZARU_", "env_file": ".env"}

    @property
    def db_url(self) -> str:
        p = Path(self.db_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{self.db_path}"

    @property
    def audio_path(self) -> Path:
        p = Path(self.audio_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def upload_path(self) -> Path:
        p = Path(self.upload_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
