"""Estimate what a workload costs with and without prompt caching and the Batch API.

Run:  uv run python -m batch_jobs.costs      (no API key needed; pure arithmetic)
Guide: guides/27_llm-apis.md section 14

Prices change: check https://platform.claude.com/docs/en/about-claude/pricing before relying on the numbers.
"""

import logging
import sys
from dataclasses import dataclass

logger = logging.getLogger(__name__)

TOKENS_PER_MILLION = 1_000_000
# Cache reads cost a tenth of normal input and 5-minute cache writes a quarter more, on most models
CACHE_READ_MULTIPLIER = 0.1
CACHE_WRITE_MULTIPLIER = 1.25
# The Batch API halves every token price, including cache reads and writes (the discounts stack)
BATCH_MULTIPLIER = 0.5


@dataclass(frozen=True)
class Prices:
    """USD per million tokens for one model."""

    input: float
    output: float


# From the pricing page on 2026-09-28
OPUS_5 = Prices(input=5.00, output=25.00)
HAIKU_4_5 = Prices(input=1.00, output=5.00)


@dataclass(frozen=True)
class Workload:
    """Many similar requests: a shared prefix (system prompt, documents) plus a unique part per request."""

    requests: int
    shared_prefix_tokens: int
    unique_input_tokens: int
    output_tokens: int


def estimate_cost(workload: Workload, prices: Prices, cached: bool = False, batch: bool = False) -> float:
    """Total USD for the workload.

    Args:
        workload: request count and tokens per request.
        prices: the model's standard prices.
        cached: the shared prefix is cached (written once, read by every later request).
        batch: sent through the Batch API.

    Returns:
        Estimated total cost in USD. Assumes every request after the first hits the cache, which is
        the best case; in a batch, cache hits are best-effort, so real savings can be a little lower.
    """
    per_token_in = prices.input / TOKENS_PER_MILLION
    per_token_out = prices.output / TOKENS_PER_MILLION
    prefix_total = workload.shared_prefix_tokens * workload.requests
    if cached:
        write = workload.shared_prefix_tokens * per_token_in * CACHE_WRITE_MULTIPLIER
        reads = workload.shared_prefix_tokens * (workload.requests - 1) * per_token_in * CACHE_READ_MULTIPLIER
        prefix_cost = write + reads
    else:
        prefix_cost = prefix_total * per_token_in
    unique_cost = workload.unique_input_tokens * workload.requests * per_token_in
    output_cost = workload.output_tokens * workload.requests * per_token_out
    total = prefix_cost + unique_cost + output_cost
    return total * BATCH_MULTIPLIER if batch else total


def comparison(workload: Workload) -> list[tuple[str, float]]:
    """The same workload priced step by step, from the most to the least expensive setup."""
    return [
        ("Opus 5, one request at a time", estimate_cost(workload, OPUS_5)),
        ("Opus 5 + prompt caching", estimate_cost(workload, OPUS_5, cached=True)),
        ("Opus 5 + caching + Batch API", estimate_cost(workload, OPUS_5, cached=True, batch=True)),
        ("Haiku 4.5 + caching + Batch API", estimate_cost(workload, HAIKU_4_5, cached=True, batch=True)),
    ]


def main() -> int:
    """Print the comparison for 10,000 requests sharing a 4,000-token instruction prefix."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    workload = Workload(
        requests=10_000, shared_prefix_tokens=4_000, unique_input_tokens=500, output_tokens=300
    )
    for label, cost in comparison(workload):
        logger.info("%-36s $%8.2f", label, cost)
    return 0


if __name__ == "__main__":
    sys.exit(main())
