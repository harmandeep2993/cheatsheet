"""Retrieval eval: is the right document in the top-k results for each question?

Guide: 34_evals-observability.md

Run:  uv run python -m docs_chatbot.evals
No API key needed: it measures retrieval only, the part that decides whether the LLM can answer at all.
"""

import json
import logging
import sys
from pathlib import Path

from docs_chatbot.chunking import load_chunks
from docs_chatbot.config import Settings
from docs_chatbot.embeddings import Embedder, HashingEmbedder
from docs_chatbot.index import VectorIndex

logger = logging.getLogger(__name__)

EVAL_FILE = Path(__file__).resolve().parent / "eval_data" / "retrieval.jsonl"
# Fail the run (and CI) if fewer than this share of questions retrieve the right document
MIN_RECALL = 0.85


def load_cases(path: Path = EVAL_FILE) -> list[dict]:
    """Read eval cases from a JSONL file."""
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def recall_at_k(index: VectorIndex, cases: list[dict], k: int) -> tuple[float, list[dict]]:
    """Share of cases whose expected source appears in the top k hits, plus the failed cases."""
    failures = []
    for case in cases:
        sources = [hit.chunk.source for hit in index.search(case["question"], k=k)]
        if case["expected_source"] not in sources:
            failures.append({**case, "got": sources})
    return 1 - len(failures) / len(cases), failures


def run(embedder: Embedder | None = None) -> float:
    """Build the index from the sample docs and report recall@k."""
    settings = Settings()
    chunks = load_chunks(settings.docs_dir, settings.chunk_chars, settings.chunk_overlap)
    index = VectorIndex.build(chunks, embedder or HashingEmbedder())
    score, failures = recall_at_k(index, load_cases(), k=settings.top_k)
    logger.info("recall@%d = %.2f over %d cases", settings.top_k, score, len(load_cases()))
    for failure in failures:
        logger.info("MISS %s: %s -> %s", failure["id"], failure["question"], failure["got"])
    return score


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sys.exit(0 if run() >= MIN_RECALL else 1)
