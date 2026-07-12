import json
import time
import httpx
from typing import Generator
from src.services.llm_provider import LLMProvider

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiClient(LLMProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        request_delay: float = 4.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key
        self.model = model
        self.request_delay = request_delay
        self.max_retries = max_retries
        self._last_request_time = 0.0

    def _headers(self) -> dict:
        return {"Content-Type": "application/json", "X-goog-api-key": self.api_key}

    def _map_messages(self, messages: list[dict]) -> list[dict]:
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            gemini_role = "model" if role == "assistant" else "user"
            contents.append({"role": gemini_role, "parts": [{"text": content}]})
        return contents

    def _wait_rate_limit(self) -> None:
        if self.request_delay <= 0:
            return
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)

    def _request(self, url: str, body: dict) -> dict:
        last_error = None
        for attempt in range(self.max_retries + 1):
            self._wait_rate_limit()
            self._last_request_time = time.time()
            try:
                resp = httpx.post(url, headers=self._headers(), json=body, timeout=120)
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Gemini request failed after {self.max_retries} retries: {e}")

            if resp.status_code in (429, 503):
                last_error = RuntimeError(f"Gemini rate limit ({resp.status_code}): {resp.text}")
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise last_error

            if resp.status_code in (400, 401, 403):
                raise RuntimeError(f"Gemini auth/error ({resp.status_code}): {resp.text}")

            resp.raise_for_status()
            return resp.json()

        raise last_error or RuntimeError("Gemini request failed")

    def chat(self, messages: list[dict], model: str | None = None) -> str:
        url = f"{GEMINI_BASE_URL}/models/{model or self.model}:generateContent"
        body = {
            "contents": self._map_messages(messages),
            "safetySettings": [
                {"category": c, "threshold": "BLOCK_NONE"}
                for c in (
                    "HARM_CATEGORY_HARASSMENT",
                    "HARM_CATEGORY_HATE_SPEECH",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "HARM_CATEGORY_DANGEROUS_CONTENT",
                )
            ],
        }
        data = self._request(url, body)
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"Gemini returned no candidates: {json.dumps(data)[:500]}")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError(f"Gemini returned no parts: {json.dumps(candidates[0])[:500]}")
        return parts[0].get("text", "")

    def stream(self, messages: list[dict], model: str | None = None) -> Generator[str, None, None]:
        url = f"{GEMINI_BASE_URL}/models/{model or self.model}:streamGenerateContent?alt=sse"
        body = {
            "contents": self._map_messages(messages),
            "safetySettings": [
                {"category": c, "threshold": "BLOCK_NONE"}
                for c in (
                    "HARM_CATEGORY_HARASSMENT",
                    "HARM_CATEGORY_HATE_SPEECH",
                    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "HARM_CATEGORY_DANGEROUS_CONTENT",
                )
            ],
        }

        last_error = None
        for attempt in range(self.max_retries + 1):
            self._wait_rate_limit()
            self._last_request_time = time.time()
            try:
                with httpx.stream("POST", url, headers=self._headers(), json=body, timeout=120) as resp:
                    if resp.status_code in (429, 503):
                        last_error = RuntimeError(f"Gemini rate limit ({resp.status_code})")
                        if attempt < self.max_retries:
                            time.sleep(2 ** attempt)
                            continue
                        raise last_error
                    if resp.status_code in (400, 401, 403):
                        text = resp.read().decode("utf-8", errors="replace")
                        raise RuntimeError(f"Gemini auth/error ({resp.status_code}): {text}")
                    resp.raise_for_status()

                    for line in resp.iter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        payload = line[6:]
                        if payload == "[DONE]":
                            return
                        try:
                            chunk = json.loads(payload)
                        except json.JSONDecodeError:
                            continue
                        candidates = chunk.get("candidates", [])
                        if not candidates:
                            continue
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for p in parts:
                            text = p.get("text", "")
                            if text:
                                yield text
                    return
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(f"Gemini stream failed after {self.max_retries} retries: {e}")

        raise last_error or RuntimeError("Gemini stream failed")

    def health_check(self) -> dict:
        if not self.api_key:
            return {"online": False, "provider": "gemini", "model": self.model, "error": "API key not set"}
        url = f"{GEMINI_BASE_URL}/models/{self.model}"
        try:
            resp = httpx.get(url, headers=self._headers(), timeout=10)
            if resp.status_code == 200:
                return {"online": True, "provider": "gemini", "model": self.model, "model_available": True}
            return {"online": False, "provider": "gemini", "model": self.model, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"online": False, "provider": "gemini", "model": self.model, "error": str(e)}

    def list_models(self) -> list[str]:
        url = f"{GEMINI_BASE_URL}/models"
        try:
            resp = httpx.get(url, headers=self._headers(), timeout=10)
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [m.get("name", "").replace("models/", "") for m in data.get("models", [])]
        except Exception:
            return []
