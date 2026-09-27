"""Routes of the documents service. The proxy mounts them under /api/documents/."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from documents_service.db import get_session
from documents_service.repositories.documents import DocumentRepository
from documents_service.schemas import DocumentCreate, DocumentOut, SearchHit
from documents_service.services.documents import DEFAULT_LIST_LIMIT, DocumentNotFoundError, DocumentService

DEFAULT_SEARCH_LIMIT = 3
MAX_SEARCH_LIMIT = 20
MAX_LIST_LIMIT = 200
QUERY_MAX_LENGTH = 500

router = APIRouter(tags=["documents"])


def get_document_service(session: Annotated[Session, Depends(get_session)]) -> DocumentService:
    """Build the service for this request; tests can override this dependency."""
    return DocumentService(DocumentRepository(session))


ServiceDep = Annotated[DocumentService, Depends(get_document_service)]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_document(payload: DocumentCreate, service: ServiceDep) -> DocumentOut:
    """Store a new document."""
    return service.create(payload)


@router.get("/")
def list_documents(
    service: ServiceDep, limit: Annotated[int, Query(ge=1, le=MAX_LIST_LIMIT)] = DEFAULT_LIST_LIMIT
) -> list[DocumentOut]:
    """Newest documents first."""
    return service.list_recent(limit)


# Declared before /{document_id} so "search" is not parsed as an id
@router.get("/search")
def search_documents(
    service: ServiceDep,
    q: Annotated[str, Query(min_length=1, max_length=QUERY_MAX_LENGTH)],
    limit: Annotated[int, Query(ge=1, le=MAX_SEARCH_LIMIT)] = DEFAULT_SEARCH_LIMIT,
) -> list[SearchHit]:
    """Keyword search, best matches first."""
    return service.search(q, limit)


@router.get("/{document_id}")
def get_document(document_id: int, service: ServiceDep) -> DocumentOut:
    """One document by id."""
    try:
        return service.get(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found") from exc
