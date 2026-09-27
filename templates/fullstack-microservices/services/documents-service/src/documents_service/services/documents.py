"""Business logic for documents: creating, listing and ranking search results."""

import re

from documents_service.repositories.documents import DocumentRepository
from documents_service.schemas import DocumentCreate, DocumentOut, SearchHit

MIN_TERM_LENGTH = 3
MAX_SEARCH_CANDIDATES = 200
DEFAULT_LIST_LIMIT = 50


class DocumentNotFoundError(Exception):
    """Raised when a document id does not exist."""


def extract_terms(query: str) -> list[str]:
    """Lowercase words from the query; short words like "a" or "is" match almost everything, so drop them."""
    words = re.findall(r"\w+", query.lower())
    return sorted({word for word in words if len(word) >= MIN_TERM_LENGTH})


class DocumentService:
    """Use cases of the documents service. Routes call these; these call the repository."""

    def __init__(self, repository: DocumentRepository):
        self._repository = repository

    def create(self, payload: DocumentCreate) -> DocumentOut:
        """Store a new document."""
        document = self._repository.add(title=payload.title.strip(), content=payload.content)
        return DocumentOut.model_validate(document)

    def get(self, document_id: int) -> DocumentOut:
        """Return one document or raise DocumentNotFoundError."""
        document = self._repository.get(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)
        return DocumentOut.model_validate(document)

    def list_recent(self, limit: int = DEFAULT_LIST_LIMIT) -> list[DocumentOut]:
        """Newest documents first."""
        return [DocumentOut.model_validate(d) for d in self._repository.list_recent(limit)]

    def search(self, query: str, limit: int) -> list[SearchHit]:
        """Rank documents by how often the query words appear in them.

        Args:
            query: free text from the user.
            limit: maximum number of hits to return.

        Returns:
            Hits sorted by score (highest first); ties keep the newest document first.
        """
        terms = extract_terms(query)
        if not terms:
            return []
        candidates = self._repository.find_containing_any(terms, MAX_SEARCH_CANDIDATES)
        hits = []
        for document in candidates:
            text = f"{document.title} {document.content}".lower()
            # Simple term-frequency score; swap for full-text search or embeddings when this is not enough
            score = sum(text.count(term) for term in terms)
            hits.append(SearchHit(id=document.id, title=document.title, content=document.content, score=score))
        hits.sort(key=lambda hit: (hit.score, hit.id), reverse=True)
        return hits[:limit]
