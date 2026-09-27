# Examples

Runnable mini-projects that put the guides into practice. Every example has tests that use a fake LLM, so **you can run all tests without an API key or any cost**. With a key, you can run the demos against the real Claude API.

| # | Folder | What it shows | Guides |
|---|---|---|---|
| 1 | `llm_basics/` | One call, streaming, structured output with Pydantic | 26 LLM APIs, 12 Pydantic |
| 2 | `tool_agent/` | Tool definitions, a manual agent loop, safe tools, step limit, error results | 28 Tool Use, 31 AI Agents |
| 3 | `docs_chatbot/` | RAG chatbot: chunking, vector index, citations, FastAPI + Uvicorn, retrieval eval, Docker | 30 RAG, 39 FastAPI, 40 Uvicorn, 42 Docker, 34 Evals |
| 4 | `mcp_server/` | MCP server exposing document search to Claude Code / Desktop / VS Code | 33 MCP |

Example 3 is the code of the step-by-step [capstone project](../97_capstone-project.md).

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
- Store vectors in Chroma or pgvector instead of NumPy ([29](../29_embeddings-vector-db.md)).
- Add streaming to `/ask` and a Streamlit UI ([38](../38_ai-ui.md)).
- Add an LLM-as-judge eval for answer faithfulness ([34](../34_evals-observability.md)).
