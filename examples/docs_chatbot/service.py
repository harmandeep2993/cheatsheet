"""Business logic of the chatbot: keeps the index and the LLM client, answers questions, re-indexes."""

import logging

from docs_chatbot.answer import Answer, generate_answer
from docs_chatbot.chunking import load_chunks
from docs_chatbot.config import Settings
from docs_chatbot.embeddings import Embedder, HashingEmbedder
from docs_chatbot.index import VectorIndex

logger = logging.getLogger(__name__)


class ChatbotService:
    """Everything the API needs, independent of HTTP (so it is easy to test and reuse)."""

    def __init__(self, settings: Settings, client, embedder: Embedder | None = None):
        self.settings = settings
        self.client = client
        self.embedder = embedder or HashingEmbedder()
        self.index = self._load_or_build()

    def _load_or_build(self) -> VectorIndex:
        path = self.settings.index_path
        if path.exists():
            logger.info("Loading index from %s", path)
            return VectorIndex.load(path, self.embedder)
        return self.reindex()

    def reindex(self) -> VectorIndex:
        """Rebuild the index from the documents folder and save it."""
        chunks = load_chunks(self.settings.docs_dir, self.settings.chunk_chars, self.settings.chunk_overlap)
        self.index = VectorIndex.build(chunks, self.embedder)
        self.index.save(self.settings.index_path)
        logger.info("Indexed %d chunks from %s", len(chunks), self.settings.docs_dir)
        return self.index

    def ask(self, question: str) -> Answer:
        """Retrieve the most relevant chunks and generate a cited answer."""
        hits = self.index.search(question, k=self.settings.top_k, min_score=self.settings.min_score)
        return generate_answer(self.client, self.settings.llm_model, self.settings.max_tokens, question, hits)
