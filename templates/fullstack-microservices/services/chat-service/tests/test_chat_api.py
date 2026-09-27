"""Chat service tests: documents-service is replaced by httpx.MockTransport and the LLM by FakeLLM."""

import httpx
from fastapi.testclient import TestClient

from chat_service.config import Settings
from chat_service.llm import FakeLLM, build_llm, build_prompt
from chat_service.main import create_app
from chat_service.schemas import SourceDocument
from chat_service.services.chat import NO_SOURCES_ANSWER
from common import REQUEST_ID_HEADER

DOCS = [
    {"id": 7, "title": "Refund policy", "content": "Refunds are paid within 5 days.", "score": 3},
    {"id": 2, "title": "Returns", "content": "Return items within 30 days.", "score": 1},
]


def make_client(handler) -> TestClient:
    settings = Settings(documents_url="http://documents.test", anthropic_api_key=None)
    app = create_app(settings, transport=httpx.MockTransport(handler), llm=FakeLLM())
    return TestClient(app)


def test_health():
    with make_client(lambda request: httpx.Response(200, json=[])) as client:
        assert client.get("/health").json()["service"] == "chat-service"


def test_ask_uses_documents_and_returns_sources():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["q"] = request.url.params["q"]
        seen["request_id"] = request.headers.get(REQUEST_ID_HEADER)
        return httpx.Response(200, json=DOCS)

    with make_client(handler) as client:
        response = client.post("/ask", json={"question": "How fast are refunds?"}, headers={REQUEST_ID_HEADER: "r1"})

    body = response.json()
    assert response.status_code == 200
    assert body["sources"] == [{"id": 7, "title": "Refund policy"}, {"id": 2, "title": "Returns"}]
    assert "Refund policy" in body["answer"]
    assert seen == {"path": "/search", "q": "How fast are refunds?", "request_id": "r1"}


def test_no_sources_skips_llm():
    with make_client(lambda request: httpx.Response(200, json=[])) as client:
        body = client.post("/ask", json={"question": "Unknown topic?"}).json()
    assert body == {"answer": NO_SOURCES_ANSWER, "sources": []}


def test_documents_error_becomes_503():
    with make_client(lambda request: httpx.Response(500)) as client:
        assert client.post("/ask", json={"question": "Anything?"}).status_code == 503


def test_documents_unreachable_becomes_503():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    with make_client(handler) as client:
        assert client.post("/ask", json={"question": "Anything?"}).status_code == 503


def test_question_is_validated():
    with make_client(lambda request: httpx.Response(200, json=[])) as client:
        assert client.post("/ask", json={"question": "?"}).status_code == 422


def test_build_prompt_numbers_sources():
    sources = [SourceDocument(id=1, title="A", content="alpha"), SourceDocument(id=2, title="B", content="beta")]
    prompt = build_prompt("Q?", sources)
    assert "[1] A\nalpha" in prompt
    assert "[2] B\nbeta" in prompt
    assert prompt.endswith("Question: Q?")


def test_build_llm_without_key_is_fake():
    assert isinstance(build_llm(Settings(anthropic_api_key=None)), FakeLLM)


def test_empty_key_from_compose_counts_as_no_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    assert Settings().anthropic_api_key is None
    assert isinstance(build_llm(Settings()), FakeLLM)
