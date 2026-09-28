"""Tests for batch_jobs with a fake client: no API key, no network, no waiting."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from batch_jobs.batch import (
    INVALID_REQUEST,
    MAX_TOKENS,
    build_requests,
    collect_results,
    normalize_label,
    run_batch,
    wait_until_ended,
)
from batch_jobs.costs import HAIKU_4_5, OPUS_5, Workload, comparison, estimate_cost
from conftest import fake_text_message


def succeeded(custom_id: str, text: str) -> SimpleNamespace:
    return SimpleNamespace(
        custom_id=custom_id, result=SimpleNamespace(type="succeeded", message=fake_text_message(text))
    )


def errored(custom_id: str, error_type: str) -> SimpleNamespace:
    # Real shape: result.error is an ErrorResponse whose .error holds the actual error type and message
    error = SimpleNamespace(type="error", error=SimpleNamespace(type=error_type, message="bad max_tokens"))
    return SimpleNamespace(custom_id=custom_id, result=SimpleNamespace(type="errored", error=error))


def other(custom_id: str, result_type: str) -> SimpleNamespace:
    return SimpleNamespace(custom_id=custom_id, result=SimpleNamespace(type=result_type))


def batch_state(status: str, processing: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        id="msgbatch_1", processing_status=status, request_counts=SimpleNamespace(processing=processing)
    )


# === Batch requests and results ===


def test_build_requests_uses_custom_ids_and_shared_settings():
    requests = build_requests({"a": "Great!", "b": "Awful."})

    assert [r["custom_id"] for r in requests] == ["a", "b"]
    assert requests[0]["params"]["messages"] == [{"role": "user", "content": "Great!"}]
    assert requests[0]["params"]["max_tokens"] == MAX_TOKENS
    assert "one word" in requests[0]["params"]["system"]


def test_wait_polls_until_ended_without_real_sleeping():
    client = MagicMock()
    client.messages.batches.retrieve.side_effect = [batch_state("in_progress", 3), batch_state("ended")]
    sleeps = []

    batch = wait_until_ended(client, "msgbatch_1", poll_seconds=5, sleep=sleeps.append)

    assert batch.processing_status == "ended"
    assert sleeps == [5]


def test_collect_results_sorts_every_result_type_by_custom_id():
    client = MagicMock()
    # Deliberately out of order: results are matched by custom_id, never by position
    client.messages.batches.results.return_value = [
        succeeded("r3", "Neutral."),
        succeeded("r1", "positive"),
        errored("r4", INVALID_REQUEST),
        errored("r5", "overloaded_error"),
        other("r6", "expired"),
        other("r7", "canceled"),
        succeeded("r2", "It is hard to say"),
    ]

    outcome = collect_results(client, "msgbatch_1")

    assert outcome.labels == {"r1": "positive", "r3": "neutral"}
    assert sorted(outcome.retry) == ["r5", "r6", "r7"]
    assert outcome.failed["r4"] == "bad max_tokens"
    assert outcome.failed["r2"].startswith("unexpected answer")


def test_run_batch_submits_waits_and_collects():
    client = MagicMock()
    client.messages.batches.create.return_value = batch_state("in_progress")
    client.messages.batches.retrieve.return_value = batch_state("ended")
    client.messages.batches.results.return_value = [succeeded("review-1", "negative")]

    batch_id, outcome = run_batch(client, {"review-1": "Broke after a week."}, sleep=lambda _: None)

    assert batch_id == "msgbatch_1"
    assert outcome.labels == {"review-1": "negative"}
    assert len(client.messages.batches.create.call_args.kwargs["requests"]) == 1


@pytest.mark.parametrize(
    ("text", "expected"), [("Positive", "positive"), (" negative. ", "negative"), ("maybe", None)]
)
def test_normalize_label(text, expected):
    assert normalize_label(text) == expected


# === Cost estimates ===

WORKLOAD = Workload(requests=10_000, shared_prefix_tokens=4_000, unique_input_tokens=500, output_tokens=300)


def test_plain_cost_matches_hand_calculation():
    # 45M input tokens * $5/M + 3M output tokens * $25/M
    assert estimate_cost(WORKLOAD, OPUS_5) == pytest.approx(300.0)


def test_batch_halves_the_price():
    assert estimate_cost(WORKLOAD, OPUS_5, batch=True) == pytest.approx(150.0)


def test_caching_reprices_the_shared_prefix():
    # One write at 1.25x plus 9,999 reads at 0.1x instead of 40M tokens at full price
    assert estimate_cost(WORKLOAD, OPUS_5, cached=True) == pytest.approx(120.0, abs=0.1)


def test_discounts_stack_and_each_step_is_cheaper():
    costs = [cost for _, cost in comparison(WORKLOAD)]
    assert costs == sorted(costs, reverse=True)
    assert costs[-1] == pytest.approx(estimate_cost(WORKLOAD, HAIKU_4_5, cached=True, batch=True))
    assert costs[0] / costs[-1] > 20
