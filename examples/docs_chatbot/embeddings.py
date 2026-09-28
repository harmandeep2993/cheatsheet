"""Text embedders. The default works offline with no model download; swap in a real model for quality.

See 30_embeddings-vector-db.md for real embedding models (sentence-transformers, Ollama, OpenAI, Voyage).
"""

from typing import Protocol

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

try:  # optional heavy dependency: pip install sentence-transformers
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# 2**18 hashed features keep collisions rare for character n-grams of small document sets
HASH_FEATURES = 2**18
CHAR_NGRAMS = (3, 5)


class Embedder(Protocol):
    """Anything that turns a list of texts into an (n, dim) array of unit-length vectors."""

    def embed(self, texts: list[str]) -> np.ndarray: ...


class HashingEmbedder:
    """Keyword-style vectors from hashed character n-grams; fast, offline, deterministic.

    Character 3- to 5-grams inside word boundaries let "jacket" match "jackets" and "return" match
    "returned". It still matches spelling, not meaning ("refund" does not match "money back"), which is
    fine for learning and tests. For semantic search use SentenceTransformerEmbedder (29_embeddings).
    """

    def __init__(self, n_features: int = HASH_FEATURES):
        self._vectorizer = HashingVectorizer(
            n_features=n_features, alternate_sign=False, norm="l2",
            analyzer="char_wb", ngram_range=CHAR_NGRAMS, lowercase=True,
        )

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return one unit-length hashed vector per text."""
        return self._vectorizer.transform(texts).toarray().astype(np.float32)


class SentenceTransformerEmbedder:
    """Semantic embeddings from a sentence-transformers model (pip install sentence-transformers)."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            raise RuntimeError("Install sentence-transformers to use SentenceTransformerEmbedder")
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        """Return one normalised semantic embedding per text."""
        return np.asarray(self._model.encode(texts, normalize_embeddings=True), dtype=np.float32)
