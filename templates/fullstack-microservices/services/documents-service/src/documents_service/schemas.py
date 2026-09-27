"""Request and response models: the public contract of this service's API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from documents_service.models import TITLE_MAX_LENGTH

CONTENT_MAX_LENGTH = 50_000


class DocumentCreate(BaseModel):
    """Body of POST /."""

    title: str = Field(min_length=1, max_length=TITLE_MAX_LENGTH)
    content: str = Field(min_length=1, max_length=CONTENT_MAX_LENGTH)


class DocumentOut(BaseModel):
    """A stored document as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    created_at: datetime


class SearchHit(BaseModel):
    """One search result; a higher score means more query words matched more often."""

    id: int
    title: str
    content: str
    score: int
