"""API and service tests for the documents service, using an in-memory SQLite database (no Docker needed)."""

import pytest
from fastapi.testclient import TestClient

from documents_service.config import Settings
from documents_service.main import create_app
from documents_service.services.documents import extract_terms


@pytest.fixture
def client():
    app = create_app(Settings(database_url="sqlite://"))
    with TestClient(app) as test_client:
        yield test_client


def add(client: TestClient, title: str, content: str) -> dict:
    response = client.post("/", json={"title": title, "content": content})
    assert response.status_code == 201
    return response.json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok", "service": "documents-service"}


def test_create_and_get(client):
    created = add(client, "Returns", "Items can be returned within 30 days.")
    fetched = client.get(f"/{created['id']}").json()
    assert fetched["title"] == "Returns"
    assert fetched["content"] == "Items can be returned within 30 days."


def test_list_is_newest_first(client):
    add(client, "First", "one")
    add(client, "Second", "two")
    assert [d["title"] for d in client.get("/").json()] == ["Second", "First"]


def test_missing_document_is_404(client):
    assert client.get("/999").status_code == 404


def test_validation_rejects_empty_title(client):
    assert client.post("/", json={"title": "", "content": "x"}).status_code == 422


def test_search_ranks_by_matching_words(client):
    add(client, "Shipping", "We ship worldwide. Shipping takes 3 to 5 days.")
    add(client, "Returns", "Return items within 30 days for a refund.")
    add(client, "Refund policy", "A refund is paid to the original card. Refund takes 5 days.")

    hits = client.get("/search", params={"q": "refund for my order"}).json()

    assert [h["title"] for h in hits] == ["Refund policy", "Returns"]
    assert hits[0]["score"] > hits[1]["score"]


def test_search_respects_limit(client):
    for number in range(5):
        add(client, f"Doc {number}", "refund")
    assert len(client.get("/search", params={"q": "refund", "limit": 2}).json()) == 2


def test_search_with_only_short_words_returns_nothing(client):
    add(client, "Doc", "a is to")
    assert client.get("/search", params={"q": "a is to"}).json() == []


def test_extract_terms_drops_short_words_and_duplicates():
    assert extract_terms("How do I RETURN a return?") == ["how", "return"]
