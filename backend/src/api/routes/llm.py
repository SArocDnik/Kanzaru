from fastapi import APIRouter
from src.config import settings
from src.services.llm_factory import get_llm_client

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/health")
def llm_health():
    client = get_llm_client()
    result = client.health_check()
    result["provider"] = settings.llm_provider
    return result


@router.get("/models")
def llm_models():
    client = get_llm_client()
    if settings.llm_provider == "gemini":
        return {
            "provider": "gemini",
            "models": [
                "gemini-flash-latest",
                "gemini-pro-latest",
                "gemini-2.5-flash",
                "gemini-2.5-pro",
            ],
        }
    return {"provider": "ollama", "models": client.list_models()}
