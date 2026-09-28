# Examples

Runnable mini-projects that put the guides into practice. Every example has tests that use a fake LLM, so **you can run all tests without an API key or any cost**. With a key, you can run the demos against the real Claude API.

| # | Folder | What it shows | Guides |
|---|---|---|---|
| 1 | `llm_basics/` | One call, streaming, structured output with Pydantic | [27 - LLM APIs](../guides/27_llm-apis.md), [13 - Pydantic](../guides/13_pydantic.md) |
| 2 | `tool_agent/` | Tool definitions, a manual agent loop, safe tools, step limit, error results | [29 - Tool Use](../guides/29_tool-use.md), [32 - AI Agents](../guides/32_ai-agents.md) |
| 3 | `docs_chatbot/` | RAG chatbot: chunking, vector index, citations, FastAPI + Uvicorn, retrieval eval, Docker | [31 - RAG](../guides/31_rag.md), [40 - FastAPI](../guides/40_fastapi.md), [41 - Uvicorn](../guides/41_uvicorn.md), [43 - Docker](../guides/43_docker.md), [35 - Evals](../guides/35_evals-observability.md) |
| 4 | `mcp_server/` | MCP server exposing document search to Claude Code / Desktop / VS Code | [34 - MCP](../guides/34_mcp.md) |
| 5 | `batch_jobs/` | Message Batches API (submit, poll, sort results by `custom_id`, resubmit failures) and a cost calculator comparing caching, batching and model choice | [27 - LLM APIs](../guides/27_llm-apis.md) |

Example 3 is the code of the step-by-step [capstone project](../guides/97_capstone-project.md).

## Setup

```bash
cd examples
uv sync                     # creates .venv and installs everything from uv.lock
uv run pytest               # all tests, no API key needed
uv run ruff check .         # lint
```

To call the real API, set your key first (never commit it):

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."      # macOS / Linux: export ANTHROPIC_API_KEY=sk-ant-...
```

## Run the demos

```bash
uv run python -m llm_basics.basics
uv run python -m tool_agent.agent "Where is order A-1042 and what is 17% of 249?"

uv run uvicorn docs_chatbot.api:app --reload          # then open http://127.0.0.1:8000/docs
uv run python -m docs_chatbot.evals                    # retrieval quality (no key needed)

uv run mcp dev mcp_server/server.py                    # MCP Inspector in the browser

uv run python -m batch_jobs.costs                      # cost comparison (no key needed)
uv run python -m batch_jobs.batch                      # real batch: 3 reviews at half price
```

Ask the chatbot from another terminal:

```bash
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question": "Can I return a jacket?"}'
```

## Docker (chatbot)

```bash
docker build -f docs_chatbot/Dockerfile -t docs-chatbot .
docker run --rm -p 8000:8000 -e ANTHROPIC_API_KEY docs-chatbot
```

## Configuration

The chatbot reads `CHATBOT_*` environment variables (see `docs_chatbot/config.py`), for example `CHATBOT_TOP_K=6` or `CHATBOT_LLM_MODEL=claude-sonnet-5`. The model for examples 1 and 2 comes from `LLM_MODEL`.

## Ideas to extend

- Swap `HashingEmbedder` for `SentenceTransformerEmbedder` (semantic search) and compare the eval score.
- Store vectors in Chroma or pgvector instead of NumPy ([30](../guides/30_embeddings-vector-db.md)).
- Add streaming to `/ask` and a Streamlit UI ([39](../guides/39_ai-ui.md)).
- Add an LLM-as-judge eval for answer faithfulness ([35](../guides/35_evals-observability.md)).
