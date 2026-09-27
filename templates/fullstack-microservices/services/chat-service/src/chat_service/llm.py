"""LLM backends: Claude when an API key is configured, otherwise a deterministic fake for offline work and tests."""

from typing import Protocol

from anthropic import AsyncAnthropic

from chat_service.config import Settings
from chat_service.schemas import SourceDocument

MAX_OUTPUT_TOKENS = 1024
FAKE_SNIPPET_CHARS = 200

SYSTEM_PROMPT = (
    "You answer questions using only the numbered sources provided. "
    "Cite sources like [1]. If the sources do not contain the answer, say you do not know."
)


class LLM(Protocol):
    """Anything that can answer a question from a list of sources."""

    async def answer(self, question: str, sources: list[SourceDocument]) -> str:
        """Return the answer text."""
        ...


def build_prompt(question: str, sources: list[SourceDocument]) -> str:
    """Numbered sources followed by the question, so the model can cite [1], [2], ..."""
    blocks = [f"[{number}] {source.title}\n{source.content}" for number, source in enumerate(sources, start=1)]
    return "Sources:\n\n" + "\n\n".join(blocks) + f"\n\nQuestion: {question}"


class ClaudeLLM:
    """Answers with Claude through the official Anthropic SDK."""

    def __init__(self, api_key: str, model: str):
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def answer(self, question: str, sources: list[SourceDocument]) -> str:
        """Send the sources and question to Claude and return the text of the reply."""
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=MAX_OUTPUT_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(question, sources)}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


class FakeLLM:
    """Offline stand-in: quotes the start of the best source. Same answer every time, which tests need."""

    async def answer(self, question: str, sources: list[SourceDocument]) -> str:
        """Return a canned answer built from the first source."""
        best = sources[0]
        return f"(offline answer) From [1] {best.title}: {best.content[:FAKE_SNIPPET_CHARS]}"


def build_llm(settings: Settings) -> LLM:
    """Pick the backend from configuration."""
    if settings.anthropic_api_key is None:
        return FakeLLM()
    return ClaudeLLM(settings.anthropic_api_key.get_secret_value(), settings.model)
