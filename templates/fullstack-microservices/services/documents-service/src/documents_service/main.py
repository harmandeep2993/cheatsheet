"""App factory for the documents service. Run with: uvicorn --factory documents_service.main:create_app"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from common import RequestIdMiddleware, health_router, setup_logging
from documents_service.api.routes import router
from documents_service.config import Settings
from documents_service.db import Base, create_db_engine, create_session_factory

SERVICE_NAME = "documents-service"

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI app. Tests pass their own Settings (for example an in-memory database)."""
    settings = settings or Settings()
    setup_logging(SERVICE_NAME, settings.log_level)
    engine = create_db_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # create_all is fine for a starter; real projects use migrations (Alembic) instead
        Base.metadata.create_all(engine)
        logger.info("documents-service ready")
        yield
        engine.dispose()

    app = FastAPI(title="Documents service", lifespan=lifespan)
    app.state.session_factory = create_session_factory(engine)
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router(SERVICE_NAME))
    app.include_router(router)
    return app
