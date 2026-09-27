"""Tests for the docs chatbot: chunking, retrieval, prompting, eval and API (no API key needed)."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from conftest import fake_text_message
from docs_chatbot.answer import NOT_FOUND, build_prompt, generate_answer
from docs_chatbot.api import app, get_service
from docs_chatbot.chunking import chunk_text, load_chunks
from docs_chatbot.config import Settings
from docs_chatbot.embeddings import HashingEmbedder
from docs_chatbot.evals import MIN_RECALL, load_cases, recall_at_k
from docs_chatbot.index import VectorIndex
from docs_chatbot.service import ChatbotService


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(index_path=tmp_path / "index.npz")


@pytest.fixture
def index(settings) -> VectorIndex:
    chunks = load_chunks(settings.docs_dir, settings.chunk_chars, settings.chunk_overlap)
    return VectorIndex.build(chunks, HashingEmbedder())


def test_chunk_text_respects_size_and_overlap():
    text = "\n\n".join(f"Paragraph {i} " + "word " * 40 for i in range(10))
    chunks = chunk_text(text, size=500, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 600 for c in chunks)
    assert chunks[1].startswith(chunks[0][-50:])


def test_search_finds_the_right_document(index):
    hits = index.search("How long do I have to return a jacket?", k=3)
    assert hits[0].chunk.source == "refund-policy.md"
    assert hits[0].score > 0


def test_index_round_trip(index, tmp_path):
    path = tmp_path / "idx.npz"
    index.save(path)
    loaded = VectorIndex.load(path, HashingEmbedder())
    assert len(loaded.chunks) == len(index.chunks)
    assert loaded.search("password reset", k=1)[0].chunk.source == "account.md"


def test_retrieval_eval_meets_threshold(index):
    score, failures = recall_at_k(index, load_cases(), k=4)
    assert score >= MIN_RECALL, failures


def test_prompt_puts_sources_first_and_question_last(index):
    hits = index.search("shipping to Austria", k=2)
    prompt = build_prompt("How long to Austria?", hits)
    assert prompt.startswith("<sources>")
    assert prompt.rstrip().endswith("Question: How long to Austria?")
    assert '<source id="1"' in prompt


def test_no_hits_skips_llm_call():
    client = MagicMock()
    answer = generate_answer(client, "model", 100, "anything", hits=[])
    assert answer.answer == NOT_FOUND
    client.messages.create.assert_not_called()


def test_service_answers_with_sources(settings):
    client = MagicMock()
    client.messages.create.return_value = fake_text_message("Jackets: 30 days if unworn [1].")
    service = ChatbotService(settings, client)

    answer = service.ask("How many days to return a jacket?")

    assert "[1]" in answer.answer
    assert answer.sources[0].source == "refund-policy.md"
    assert settings.index_path.exists()


def test_api_endpoints(settings):
    client = MagicMock()
    client.messages.create.return_value = fake_text_message("Free over 50 EUR [1].")
    service = ChatbotService(settings, client)
    app.dependency_overrides[get_service] = lambda: service
    try:
        # No "with": lifespan (which needs a real API key) is skipped in tests
        http = TestClient(app)
        assert http.get("/health").json() == {"status": "ok"}
        r = http.post("/ask", json={"question": "Is shipping free?"})
        assert r.status_code == 200
        assert r.json()["sources"][0]["source"] == "shipping.md"
        assert http.post("/ask", json={"question": "x"}).status_code == 422
        assert http.post("/reindex").json()["chunks"] > 0
    finally:
        app.dependency_overrides.clear()
