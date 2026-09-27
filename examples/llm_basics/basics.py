"""Minimal Claude API calls: a single question, a streamed answer and structured output with Pydantic.

Run:  uv run python -m llm_basics.basics      (needs ANTHROPIC_API_KEY)
Guide: 26_llm-apis.md, 12_pydantic.md
"""

import logging
import os
import sys
from collections.abc import Iterator
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

MODEL = os.getenv("LLM_MODEL", "claude-opus-5")
MAX_TOKENS = 16000
# Classification answers are short; a smaller cap keeps cost predictable
CLASSIFY_MAX_TOKENS = 1024
DEFAULT_SYSTEM = "You are a concise assistant. Answer in at most three sentences."


class Ticket(BaseModel):
    """Structured classification of a customer support message."""

    category: Literal["billing", "technical", "shipping", "other"]
    urgency: int = Field(ge=1, le=5, description="1 = can wait, 5 = critical")
    summary: str = Field(description="One-sentence summary of the problem")


def text_of(response) -> str:
    """Join the text blocks of a response, skipping thinking and tool blocks."""
    return "".join(block.text for block in response.content if block.type == "text")


def ask(client, question: str, system: str = DEFAULT_SYSTEM) -> str:
    """Send one question and return the answer text.

    Args:
        client: an anthropic.Anthropic client (or a test double with the same interface).
        question: the user's question.
        system: system prompt that sets behaviour.

    Returns:
        The model's answer as plain text.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    if response.stop_reason == "max_tokens":
        logger.warning("Answer was cut off at max_tokens; raise the limit or stream")
    return text_of(response)


def stream_answer(client, question: str) -> Iterator[str]:
    """Yield the answer piece by piece as the model generates it."""
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": question}],
    ) as stream:
        yield from stream.text_stream


def classify_ticket(client, message: str) -> Ticket:
    """Classify a support message into a validated Ticket using structured outputs."""
    response = client.messages.parse(
        model=MODEL,
        max_tokens=CLASSIFY_MAX_TOKENS,
        messages=[{"role": "user", "content": f"Classify this support message:\n\n{message}"}],
        output_format=Ticket,
    )
    return response.parsed_output


def main() -> None:
    """Demo all three calls against the real API."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    client = anthropic.Anthropic()

    logger.info("== ask ==")
    logger.info(ask(client, "What is retrieval-augmented generation?"))

    logger.info("== stream ==")
    for chunk in stream_answer(client, "Give three tips for writing good prompts."):
        sys.stdout.write(chunk)
        sys.stdout.flush()
    sys.stdout.write("\n")

    logger.info("== structured output ==")
    ticket = classify_ticket(client, "I was charged twice for order A-1042 and need a refund today!")
    logger.info(ticket.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
