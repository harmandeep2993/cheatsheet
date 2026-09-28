"""MCP server that lets Claude Code, Claude Desktop or VS Code search the sample documents.

Test:     uv run mcp dev mcp_server/server.py
Connect:  claude mcp add pocket-docs -- uv --directory <path-to-examples> run python -m mcp_server.server
Guide:    34_mcp.md
"""

import logging
from functools import lru_cache

from mcp.server.mcpserver import MCPServer

from docs_chatbot.chunking import load_chunks
from docs_chatbot.config import Settings
from docs_chatbot.embeddings import HashingEmbedder
from docs_chatbot.index import VectorIndex

# stdio transport uses stdout for the protocol, so logs must go to stderr (logging's default)
logger = logging.getLogger(__name__)
MAX_RESULTS = 10

mcp = MCPServer("pocket-docs")


@lru_cache(maxsize=1)
def get_index() -> VectorIndex:
    """Build the index once, on first use."""
    settings = Settings()
    chunks = load_chunks(settings.docs_dir, settings.chunk_chars, settings.chunk_overlap)
    logger.info("Indexed %d chunks", len(chunks))
    return VectorIndex.build(chunks, HashingEmbedder())


@mcp.tool()
def search_docs(query: str, k: int = 3) -> str:
    """Search the Acme Outdoor help documents (refunds, shipping, account) and return matching passages.

    Args:
        query: What to look for, in plain words.
        k: Number of passages to return (1 to 10).
    """
    hits = get_index().search(query, k=max(1, min(k, MAX_RESULTS)))
    if not hits:
        return "No matching passages."
    return "\n\n".join(f"[{h.chunk.source} | score {h.score:.2f}]\n{h.chunk.text}" for h in hits)


@mcp.tool()
def list_documents() -> list[str]:
    """List the help documents that can be searched."""
    return sorted({chunk.source for chunk in get_index().chunks})


@mcp.prompt()
def answer_from_docs(question: str) -> str:
    """Prompt template: answer a customer question using search_docs and cite the files."""
    return (f"Use the search_docs tool to find passages about: {question}\n"
            "Answer using only those passages and cite the file names.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mcp.run()
