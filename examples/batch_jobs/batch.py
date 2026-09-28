"""Classify many reviews with the Message Batches API: build requests, submit, wait, collect by custom_id.

Run:  uv run python -m batch_jobs.batch   (needs ANTHROPIC_API_KEY; a real batch at 50% of standard price)
Guide: guides/27_llm-apis.md sections 13 and 14
"""

import logging
import os
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

logger = logging.getLogger(__name__)

# A one-word label is easy work: a small model is plenty, and together with the batch discount
# it costs a small fraction of a large model called one request at a time
MODEL = os.getenv("BATCH_MODEL", "claude-haiku-4-5")
# Backstop only: the answer is one word
MAX_TOKENS = 64
# Most batches finish within an hour; checking every minute is frequent enough and cheap
POLL_SECONDS = 60
LABELS = ("positive", "negative", "neutral")
SYSTEM_PROMPT = (
    "Classify the sentiment of the customer review. "
    "Answer with exactly one word: positive, negative or neutral."
)
# The kind of error nested inside an errored result that retrying cannot fix
INVALID_REQUEST = "invalid_request_error"

DEMO_REVIEWS = {
    "review-1": "The jacket fits perfectly and arrived a day early.",
    "review-2": "Broke after two washes. Support never answered my emails.",
    "review-3": "It is a normal t-shirt. Nothing special, nothing wrong.",
}


@dataclass
class BatchOutcome:
    """What came back from a finished batch, sorted into what to keep, retry or fix."""

    labels: dict[str, str] = field(default_factory=dict)
    retry: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)


def build_requests(items: dict[str, str]) -> list[Request]:
    """One batch request per item; the custom_id is how each result is matched back to its item.

    Args:
        items: custom_id -> review text. IDs must be unique within the batch.

    Returns:
        Requests ready for client.messages.batches.create.
    """
    return [
        Request(
            custom_id=custom_id,
            params=MessageCreateParamsNonStreaming(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": text}],
            ),
        )
        for custom_id, text in items.items()
    ]


def submit(client, items: dict[str, str]) -> str:
    """Create the batch and return its ID. Store the ID: it is all you need to fetch results later."""
    batch = client.messages.batches.create(requests=build_requests(items))
    logger.info("Submitted batch %s with %d requests", batch.id, len(items))
    return batch.id


def wait_until_ended(client, batch_id: str, poll_seconds: float = POLL_SECONDS, sleep: Callable = time.sleep):
    """Poll until processing_status is "ended" and return the final batch object.

    "ended" means every request finished one way or another (succeeded, errored, expired or canceled),
    not that all of them succeeded; check the results.
    """
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            return batch
        logger.info("Batch %s: %d still processing", batch_id, batch.request_counts.processing)
        sleep(poll_seconds)


def normalize_label(text: str) -> str | None:
    """The label if the answer is one of LABELS (ignoring case and punctuation), otherwise None."""
    word = text.strip().strip(".!").lower()
    return word if word in LABELS else None


def collect_results(client, batch_id: str) -> BatchOutcome:
    """Read every result and sort it. Results arrive in any order, so everything is keyed by custom_id."""
    outcome = BatchOutcome()
    for item in client.messages.batches.results(batch_id):
        result = item.result
        if result.type == "succeeded":
            text = "".join(b.text for b in result.message.content if b.type == "text")
            label = normalize_label(text)
            if label is None:
                outcome.failed[item.custom_id] = f"unexpected answer: {text!r}"
            else:
                outcome.labels[item.custom_id] = label
        elif result.type == "errored" and result.error.error.type == INVALID_REQUEST:
            # The request itself is wrong (bad parameters); sending it again fails the same way
            outcome.failed[item.custom_id] = result.error.error.message
        else:
            # Server errors, expired (not processed within 24 hours) and canceled requests can be resubmitted
            outcome.retry.append(item.custom_id)
    return outcome


def run_batch(
    client, items: dict[str, str], poll_seconds: float = POLL_SECONDS, sleep: Callable = time.sleep
):
    """Submit, wait and collect in one call. Returns the batch ID and the sorted outcome."""
    batch_id = submit(client, items)
    wait_until_ended(client, batch_id, poll_seconds, sleep)
    return batch_id, collect_results(client, batch_id)


def main() -> int:
    """Classify the demo reviews with a real batch and print the labels."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    client = anthropic.Anthropic()
    batch_id, outcome = run_batch(client, DEMO_REVIEWS)
    logger.info("Batch %s finished", batch_id)
    for custom_id in sorted(outcome.labels):
        logger.info("%s: %s", custom_id, outcome.labels[custom_id])
    if outcome.retry:
        logger.warning("Resubmit these in a new batch: %s", ", ".join(outcome.retry))
    for custom_id, reason in outcome.failed.items():
        logger.error("%s failed: %s", custom_id, reason)
    return 0 if not outcome.failed and not outcome.retry else 1


if __name__ == "__main__":
    sys.exit(main())
