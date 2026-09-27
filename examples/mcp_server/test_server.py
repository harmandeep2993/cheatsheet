"""Tests for the MCP server tools, called directly as Python functions."""

from mcp_server.server import answer_from_docs, list_documents, search_docs


def test_list_documents():
    assert list_documents() == ["account.md", "refund-policy.md", "shipping.md"]


def test_search_docs_returns_relevant_passage():
    result = search_docs("reset my password", k=1)
    assert result.startswith("[account.md")


def test_search_docs_clamps_k():
    assert search_docs("shipping", k=500).count("[") <= 10


def test_prompt_mentions_tool():
    assert "search_docs" in answer_from_docs("refund for jackets")
