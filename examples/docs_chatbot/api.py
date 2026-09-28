"""HTTP API for the chatbot. Routes only validate input, call the service and return.

Run:  uv run uvicorn docs_chatbot.api:app --reload      (needs ANTHROPIC_API_KEY for /ask)
Docs: http://127.0.0.1:8000/docs
Guide: 40_fastapi.md, 41_uvicorn.md
"""

from contextlib import asynccontextmanager
from typing import Annotated

import anthropic
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel, Field

from docs_chatbot.answer import Answer
from docs_chatbot.config import Settings
from docs_chatbot.service import ChatbotService

MAX_QUESTION_CHARS = 2000


class AskRequest(BaseModel):
    """A user question."""

    question: str = Field(min_length=3, max_length=MAX_QUESTION_CHARS)


class IndexStatus(BaseModel):
    """Result of a re-index."""

    chunks: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the shared service once per worker at startup."""
    # Build (or load) the index once per worker at startup, not on every request
    app.state.service = ChatbotService(Settings(), anthropic.Anthropic())
    yield


app = FastAPI(title="Docs Chatbot", version="1.0.0", lifespan=lifespan)


def get_service(request: Request) -> ChatbotService:
    """Dependency that hands the shared service to routes (overridden in tests)."""
    return request.app.state.service


Service = Annotated[ChatbotService, Depends(get_service)]


@app.get("/health")
def health() -> dict:
    """Liveness / readiness probe."""
    return {"status": "ok"}


@app.post("/ask", response_model=Answer)
def ask(body: AskRequest, service: Service) -> Answer:
    """Answer a question from the documents, with sources."""
    return service.ask(body.question)


@app.post("/reindex", response_model=IndexStatus)
def reindex(service: Service) -> IndexStatus:
    """Rebuild the index after documents changed."""
    return IndexStatus(chunks=len(service.reindex().chunks))
