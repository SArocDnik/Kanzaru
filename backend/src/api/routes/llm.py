from fastapi import APIRouter
from src.config import settings
from src.services.llm_client import LLMClient

router = APIRouter(prefix="/llm", tags=["llm"])

_client = LLMClient(url=settings.ollama_url, model=settings.ollama_model)


@router.get("/health")
def llm_health():
    return _client.health_check()


@router.get("/models")
def llm_models():
    return {"models": _client.list_models()}
