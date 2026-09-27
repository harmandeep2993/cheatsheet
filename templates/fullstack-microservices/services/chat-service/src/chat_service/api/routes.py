"""Routes of the chat service. The proxy mounts them under /api/chat/."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from chat_service.clients.documents import DocumentsUnavailableError
from chat_service.schemas import AskRequest, ChatAnswer
from chat_service.services.chat import ChatService

router = APIRouter(tags=["chat"])


def get_chat_service(request: Request) -> ChatService:
    """The ChatService built at startup; tests can override this dependency."""
    return request.app.state.chat_service


@router.post("/ask")
async def ask(payload: AskRequest, service: Annotated[ChatService, Depends(get_chat_service)]) -> ChatAnswer:
    """Answer a question from the stored documents."""
    try:
        return await service.ask(payload.question)
    except DocumentsUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Documents service is unavailable"
        ) from exc
