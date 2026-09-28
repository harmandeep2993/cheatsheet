"""A small in-memory vector index with save / load (see 30_embeddings-vector-db.md section 4)."""

import json
from pathlib import Path

import numpy as np
from pydantic import BaseModel

from docs_chatbot.chunking import Chunk
from docs_chatbot.embeddings import Embedder


class Hit(BaseModel):
    """A retrieved chunk and its cosine similarity to the query."""

    chunk: Chunk
    score: float


class VectorIndex:
    """Stores chunk vectors in a NumPy matrix; search is one matrix multiplication (exact cosine)."""

    def __init__(self, embedder: Embedder, chunks: list[Chunk], vectors: np.ndarray):
        self.embedder = embedder
        self.chunks = chunks
        self.vectors = vectors

    @classmethod
    def build(cls, chunks: list[Chunk], embedder: Embedder) -> "VectorIndex":
        """Embed all chunks and create an index."""
        vectors = embedder.embed([c.text for c in chunks]) if chunks else np.zeros((0, 1), np.float32)
        return cls(embedder, chunks, vectors)

    def search(self, query: str, k: int, min_score: float = 0.0) -> list[Hit]:
        """Return the k most similar chunks with a score of at least min_score."""
        if not self.chunks:
            return []
        query_vec = self.embedder.embed([query])[0]
        # Vectors are unit length, so the dot product is the cosine similarity
        scores = self.vectors @ query_vec
        best = np.argsort(-scores)[:k]
        return [Hit(chunk=self.chunks[i], score=float(scores[i])) for i in best if scores[i] >= min_score]

    def save(self, path: Path) -> None:
        """Write vectors (.npz) and chunk metadata (.json) next to each other."""
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(path, vectors=self.vectors)
        path.with_suffix(".json").write_text(
            json.dumps([c.model_dump() for c in self.chunks], ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path, embedder: Embedder) -> "VectorIndex":
        """Load an index saved with save(); the embedder must be the one used to build it."""
        vectors = np.load(path)["vectors"]
        chunks = [Chunk(**c) for c in json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))]
        return cls(embedder, chunks, vectors)
