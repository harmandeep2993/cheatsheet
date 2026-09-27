"""Business logic: find sources for a question, then ask the LLM to answer from them."""

from chat_service.clients.documents import DocumentsClient
from chat_service.llm import LLM
from chat_service.schemas import ChatAnswer, SourceRef

NO_SOURCES_ANSWER = "I could not find anything about that in the documents."


class ChatService:
    """Answers questions. Depends on interfaces (client, LLM) so tests can swap in fakes."""

    def __init__(self, documents: DocumentsClient, llm: LLM, max_sources: int):
        self._documents = documents
        self._llm = llm
        self._max_sources = max_sources

    async def ask(self, question: str) -> ChatAnswer:
        """Answer the question with sources.

        Raises:
            DocumentsUnavailableError: when documents-service cannot be reached.
        """
        sources = await self._documents.search(question, self._max_sources)
        # Skip the LLM call entirely when there is nothing to ground the answer in: cheaper and no guessing
        if not sources:
            return ChatAnswer(answer=NO_SOURCES_ANSWER, sources=[])
        text = await self._llm.answer(question, sources)
        return ChatAnswer(answer=text, sources=[SourceRef(id=s.id, title=s.title) for s in sources])
