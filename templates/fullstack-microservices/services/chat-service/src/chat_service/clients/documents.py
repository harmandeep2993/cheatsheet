"""Client for documents-service: the only place that knows its URLs and response format."""

import logging

import httpx

from chat_service.schemas import SourceDocument
from common import REQUEST_ID_HEADER, current_request_id

logger = logging.getLogger(__name__)


class DocumentsUnavailableError(Exception):
    """documents-service could not be reached or returned an error."""


class DocumentsClient:
    """Calls documents-service over HTTP using a shared httpx.AsyncClient (base URL, timeout, retries)."""

    def __init__(self, http: httpx.AsyncClient):
        self._http = http

    async def search(self, query: str, limit: int) -> list[SourceDocument]:
        """Best matching documents for the query.

        Raises:
            DocumentsUnavailableError: on timeouts, connection errors or non-2xx responses.
        """
        # Forward the request ID so one user request can be followed across both services' logs
        request_id = current_request_id()
        headers = {REQUEST_ID_HEADER: request_id} if request_id else {}
        try:
            response = await self._http.get("/search", params={"q": query, "limit": limit}, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("documents-service search failed: %s", exc)
            raise DocumentsUnavailableError(str(exc)) from exc
        return [SourceDocument.model_validate(item) for item in response.json()]
