"""Shared infrastructure for every service. Business logic never goes here; it belongs to one service."""

from common.health import health_router
from common.logging import setup_logging
from common.middleware import REQUEST_ID_HEADER, RequestIdMiddleware, current_request_id
from common.settings import ServiceSettings

__all__ = [
    "REQUEST_ID_HEADER",
    "RequestIdMiddleware",
    "ServiceSettings",
    "current_request_id",
    "health_router",
    "setup_logging",
]
