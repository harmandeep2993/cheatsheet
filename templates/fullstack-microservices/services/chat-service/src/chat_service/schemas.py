"""Request and response models of the chat API, plus the document shape it receives from documents-service."""

from pydantic import BaseModel, Field

QUESTION_MAX_LENGTH = 2000


class AskRequest(BaseModel):
    """Body of POST /ask."""

    question: str = Field(min_length=3, max_length=QUESTION_MAX_LENGTH)


class SourceDocument(BaseModel):
    """A search hit returned by documents-service (only the fields this service needs)."""

    id: int
    title: str
    content: str


class SourceRef(BaseModel):
    """A source shown to the user under the answer."""

    id: int
    title: str


class ChatAnswer(BaseModel):
    """Response of POST /ask."""

    answer: str
    sources: list[SourceRef]
