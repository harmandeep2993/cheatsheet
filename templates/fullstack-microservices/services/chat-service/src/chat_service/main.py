"""App factory for the chat service. Run with: uvicorn --factory chat_service.main:create_app"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from chat_service.api.routes import router
from chat_service.clients.documents import DocumentsClient
from chat_service.config import Settings
from chat_service.llm import LLM, build_llm
from chat_service.services.chat import ChatService
from common import RequestIdMiddleware, health_router, setup_logging

SERVICE_NAME = "chat-service"
# Retries only repeat failed connection attempts (safe); they never resend a request the server received
CONNECT_RETRIES = 2

logger = logging.getLogger(__name__)


def create_app(
    settings: Settings | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
    llm: LLM | None = None,
) -> FastAPI:
    """Build the FastAPI app.

    Args:
        settings: configuration; read from the environment when omitted.
        transport: httpx transport for documents-service; tests pass httpx.MockTransport.
        llm: LLM backend; chosen from settings when omitted.
    """
    settings = settings or Settings()
    setup_logging(SERVICE_NAME, settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # One pooled client for the whole process: reusing connections is much faster than one per request
        async with httpx.AsyncClient(
            base_url=settings.documents_url,
            timeout=settings.request_timeout_seconds,
            transport=transport or httpx.AsyncHTTPTransport(retries=CONNECT_RETRIES),
        ) as http:
            app.state.chat_service = ChatService(
                DocumentsClient(http), llm or build_llm(settings), settings.max_sources
            )
            logger.info("chat-service ready, documents at %s", settings.documents_url)
            yield

    app = FastAPI(title="Chat service", lifespan=lifespan)
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router(SERVICE_NAME))
    app.include_router(router)
    return app
