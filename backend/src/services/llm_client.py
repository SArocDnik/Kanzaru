import httpx
import ollama
from typing import Generator
from src.services.llm_provider import LLMProvider


class LLMClient(LLMProvider):
    def __init__(self, url: str = "http://localhost:11434", model: str = "qwen2.5:7b"):
        self.url = url
        self.model = model

    def health_check(self) -> dict:
        try:
            resp = httpx.get(f"{self.url}/api/tags", timeout=5)
            if resp.status_code != 200:
                return {"online": False, "model_available": False, "models": []}
            models = [m["name"] for m in resp.json().get("models", [])]
            return {
                "online": True,
                "model_available": self.model in models,
                "models": models,
            }
        except Exception:
            return {"online": False, "model_available": False, "models": []}

    def list_models(self) -> list[str]:
        resp = httpx.get(f"{self.url}/api/tags", timeout=5)
        if resp.status_code != 200:
            return []
        return [m["name"] for m in resp.json().get("models", [])]

    def chat(self, messages: list[dict], model: str | None = None) -> str:
        client = ollama.Client(host=self.url)
        resp = client.chat(model=model or self.model, messages=messages)
        return resp["message"]["content"]

    def stream(self, messages: list[dict], model: str | None = None) -> Generator[str, None, None]:
        client = ollama.Client(host=self.url)
        for chunk in client.chat(model=model or self.model, messages=messages, stream=True):
            yield chunk["message"]["content"]
