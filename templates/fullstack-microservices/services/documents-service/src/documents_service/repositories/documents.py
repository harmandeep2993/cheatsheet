"""Database access for documents. No business rules here, only queries."""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from documents_service.models import Document


class DocumentRepository:
    """Reads and writes Document rows through one SQLAlchemy session."""

    def __init__(self, session: Session):
        self._session = session

    def add(self, title: str, content: str) -> Document:
        """Insert a document and return it with its new id."""
        document = Document(title=title, content=content)
        self._session.add(document)
        self._session.commit()
        self._session.refresh(document)
        return document

    def get(self, document_id: int) -> Document | None:
        """Return one document or None."""
        return self._session.get(Document, document_id)

    def list_recent(self, limit: int) -> list[Document]:
        """Newest documents first."""
        query = select(Document).order_by(Document.id.desc()).limit(limit)
        return list(self._session.scalars(query))

    def find_containing_any(self, terms: list[str], limit: int) -> list[Document]:
        """Documents whose title or content contains at least one of the (lowercase) terms."""
        conditions = [
            or_(func.lower(Document.title).contains(term), func.lower(Document.content).contains(term))
            for term in terms
        ]
        query = select(Document).where(or_(*conditions)).limit(limit)
        return list(self._session.scalars(query))
