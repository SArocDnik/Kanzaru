from typing import Generator, Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    def chat(self, messages: list[dict], model: str | None = None) -> str:
        ...

    def stream(self, messages: list[dict], model: str | None = None) -> Generator[str, None, None]:
        ...

    def health_check(self) -> dict:
        ...
