"""Load Markdown / text documents and split them into overlapping chunks (see 31_rag.md sections 2-6)."""

import re
from pathlib import Path

from pydantic import BaseModel

SUPPORTED_SUFFIXES = {".md", ".txt"}


class Chunk(BaseModel):
    """One retrievable piece of a document, with metadata for citations."""

    id: str
    source: str
    title: str
    text: str


def clean(text: str) -> str:
    """Normalise whitespace so chunk sizes and embeddings are consistent."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text on paragraph boundaries into chunks of about `size` characters.

    Paragraphs are merged until the size limit; the last `overlap` characters of a chunk are repeated
    at the start of the next one so ideas are not cut in half.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}" if current else para
            continue
        if current:
            chunks.append(current)
            current = f"{current[-overlap:]}\n\n{para}" if overlap else para
        else:
            current = para
        # A single paragraph longer than the limit is split hard
        while len(current) > size:
            chunks.append(current[:size])
            current = current[size - overlap:]
    if current:
        chunks.append(current)
    return chunks


def document_title(text: str, fallback: str) -> str:
    """Use the first Markdown heading as the title, else the file name."""
    match = re.search(r"^#\s+(.+)$", text, re.M)
    return match.group(1).strip() if match else fallback


def load_chunks(docs_dir: Path, size: int, overlap: int) -> list[Chunk]:
    """Read every supported file in docs_dir and return its chunks with stable IDs."""
    chunks: list[Chunk] = []
    for path in sorted(docs_dir.rglob("*")):
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        text = clean(path.read_text(encoding="utf-8"))
        title = document_title(text, path.stem)
        for i, piece in enumerate(chunk_text(text, size, overlap)):
            # Title in the chunk text helps retrieval when a chunk alone is ambiguous
            chunks.append(Chunk(id=f"{path.name}::{i}", source=path.name, title=title,
                                text=f"{title}\n\n{piece}" if i else piece))
    return chunks
