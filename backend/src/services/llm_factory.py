from src.config import settings
from src.services.llm_provider import LLMProvider
from src.services.llm_client import LLMClient
from src.services.gemini_client import GeminiClient


def get_llm_client(quality: bool = False) -> LLMProvider:
    if settings.llm_provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("KANZARU_GEMINI_API_KEY not set. Set it in .env or switch to KANZARU_LLM_PROVIDER=ollama")
        model = settings.gemini_quality_model if quality else settings.gemini_model
        return GeminiClient(
            api_key=settings.gemini_api_key,
            model=model,
            request_delay=settings.gemini_request_delay,
            max_retries=settings.gemini_max_retries,
        )
    return LLMClient(url=settings.ollama_url, model=settings.ollama_model)
