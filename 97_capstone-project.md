# 97 - Capstone Project: Document Chatbot

<!-- nav:start -->
**Previous:** [48 - Azure VM + Linux + Ollama](48_azure-vm-ollama.md) | **Index:** [All guides](README.md) | **Next:** [98 - Glossary](98_glossary.md)
<!-- nav:end -->

Build a real AI application end to end: a chatbot that answers questions from your documents with citations, served as an API, tested, evaluated, containerised, automated with CI and deployed to Azure. The finished code is in `examples/docs_chatbot/` ([examples overview](examples/README.md)); this page explains every step and links each one to the guide behind it.

## Contents

1. [What You Will Build](#1-what-you-will-build)
2. [Prerequisites](#2-prerequisites)
3. [Step 1: Set Up the Project](#3-step-1-set-up-the-project)
4. [Step 2: Load and Chunk Documents](#4-step-2-load-and-chunk-documents)
5. [Step 3: Embed and Index](#5-step-3-embed-and-index)
6. [Step 4: Answer with Citations](#6-step-4-answer-with-citations)
7. [Step 5: Service Layer and Settings](#7-step-5-service-layer-and-settings)
8. [Step 6: HTTP API with FastAPI and Uvicorn](#8-step-6-http-api-with-fastapi-and-uvicorn)
9. [Step 7: Test Everything](#9-step-7-test-everything)
10. [Step 8: Measure Retrieval Quality](#10-step-8-measure-retrieval-quality)
11. [Step 9: Containerise with Docker](#11-step-9-containerise-with-docker)
12. [Step 10: Automate with GitHub Actions](#12-step-10-automate-with-github-actions)
13. [Step 11: Deploy to Azure Container Apps](#13-step-11-deploy-to-azure-container-apps)
14. [Step 12: Add a Chat UI](#14-step-12-add-a-chat-ui)
15. [Step 13: Expose It to AI Tools with MCP](#15-step-13-expose-it-to-ai-tools-with-mcp)
16. [Upgrade Path](#16-upgrade-path)
17. [What You Practised](#17-what-you-practised)
18. [Troubleshooting](#18-troubleshooting)

---

## 1. What You Will Build

> A support chatbot for a fictional outdoor shop that answers from its help documents. Retrieval-augmented generation: find the relevant passages, give them to Claude, answer with numbered citations. Use it as a portfolio project and a template for "chat with our documents" at work.

```text
                       INDEXING (startup / POST /reindex)
docs/*.md --load + chunk--> chunks --embed--> vectors --> VectorIndex (NumPy) --save--> .index/index.npz
[04 Step 2]                          [05 Step 3]

                       ASKING (POST /ask)
client --HTTP--> Uvicorn --> FastAPI route --> ChatbotService.ask()
                 [40]        [39] + Pydantic      |
                                                  +--> index.search(question) -> top-k chunks   [29] [30]
                                                  +--> build_prompt(sources first, question last) [27]
                                                  +--> Claude messages.create -> answer [n]       [26]
                 <-- JSON {answer, sources[]} ----+

Around it: tests with a fake LLM [14], retrieval eval [34], Docker [42], CI [43], Azure [47], MCP [33]
```

| File | Responsibility |
|---|---|
| `config.py` | All settings, validated, from `CHATBOT_*` env vars |
| `chunking.py` | Load `.md` / `.txt` files, clean, split into overlapping chunks |
| `embeddings.py` | Turn text into unit vectors (offline hashing default, optional semantic model) |
| `index.py` | Store vectors, cosine search, save / load |
| `answer.py` | Prompt with numbered sources, call Claude, return answer + sources |
| `service.py` | Business logic that ties it together (no HTTP code) |
| `api.py` | Thin FastAPI routes: validate, call the service, return |
| `evals.py` | Recall@k on a small question set |
| `test_chatbot.py` | Unit and API tests with a fake LLM |
| `Dockerfile` | Production image run by Uvicorn |

## 2. Prerequisites

> Tools and knowledge you need before starting. Install the tools once; skim the linked guides. Use it before Step 1.

- Tools: Git ([04](04_git.md)), uv ([11](11_uv.md)), VS Code ([05](05_vscode.md)), Docker ([42](42_docker.md)); Azure CLI for Step 11 ([47](47_azure.md)).
- An Anthropic API key for real answers ([26](26_llm-apis.md) section 1). Tests and evals work without one.
- Background reading: [25 - LLM Fundamentals](25_llm-fundamentals.md), [30 - RAG](30_rag.md).

## 3. Step 1: Set Up the Project

> A uv project with locked dependencies and a clean folder structure. `uv init`, `uv add` the libraries, add dev tools, create the package folder. Use it for the start of any Python service. Guides: [11 - uv](11_uv.md), [10 - venv](10_python-virtual-environment.md).

```bash
git clone https://github.com/harmandeep2993/pocket-guide.git
cd pocket-guide/examples
uv sync                      # installs the exact versions from uv.lock
uv run pytest                # everything should pass before you change anything
```

Building it yourself from scratch instead:

```bash
uv init docs-chatbot && cd docs-chatbot
uv add anthropic fastapi "uvicorn[standard]" pydantic pydantic-settings numpy scikit-learn
uv add --dev pytest ruff
mkdir docs_chatbot docs_chatbot/docs
```

Put `ANTHROPIC_API_KEY` in a git-ignored `.env` or your shell, never in code ([07](07_yaml-json.md) section 11).

## 4. Step 2: Load and Chunk Documents

> Turn documents into retrievable pieces with metadata. Read each file, normalise whitespace, split on paragraph boundaries into ~1,200-character chunks with 200 characters of overlap, keep file name and title for citations. Use it as the first stage of every RAG system. Guide: [30 - RAG](30_rag.md) sections 2-6.

`chunking.py` (key part):

```python
def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}" if current else para
            continue
        if current:
            chunks.append(current)
            current = f"{current[-overlap:]}\n\n{para}" if overlap else para   # overlap keeps context
        ...
```

Each chunk becomes a Pydantic `Chunk(id="refund-policy.md::0", source=..., title=..., text=...)`. Stable IDs make updates and citations easy.

Try it: add your own `.md` file to `docs_chatbot/docs/`, then check `load_chunks(...)` in a Python shell.

## 5. Step 3: Embed and Index

> Convert chunks to vectors and search them by similarity. An `Embedder` turns text into unit-length vectors; `VectorIndex` stores them in a NumPy matrix; search is one matrix multiplication (cosine similarity) followed by top-k. Use it in every retrieval step. Guide: [29 - Embeddings and Vector DBs](29_embeddings-vector-db.md) sections 1-4.

```python
class VectorIndex:
    def search(self, query: str, k: int, min_score: float = 0.0) -> list[Hit]:
        query_vec = self.embedder.embed([query])[0]
        scores = self.vectors @ query_vec          # unit vectors: dot product = cosine
        best = np.argsort(-scores)[:k]
        return [Hit(chunk=self.chunks[i], score=float(scores[i])) for i in best if scores[i] >= min_score]
```

The default `HashingEmbedder` hashes character 3- to 5-grams: it works offline, needs no model download and is deterministic, which keeps tests and CI fast. It matches **spelling, not meaning**: "jacket" finds "jackets", but "money back" does not find "refund". That limitation is deliberate so you can see the difference a real embedding model makes (section 16).

## 6. Step 4: Answer with Citations

> Ask Claude to answer only from the retrieved passages and cite them. Numbered `<source>` tags first, question last; a system prompt that forbids outside knowledge and defines the "not found" reply; skip the LLM entirely when nothing relevant was retrieved. Use it in any grounded Q&A. Guides: [27 - Prompt Engineering](27_prompt-engineering.md) sections 4, 9, 10; [26 - LLM APIs](26_llm-apis.md).

```python
SYSTEM_PROMPT = (
    "You answer questions using only the numbered sources provided. "
    "Cite sources after each claim like [1] or [1][2]. "
    "If the sources do not contain the answer, reply exactly: "
    "\"I could not find that in the documentation.\" Do not use outside knowledge."
)

response = client.messages.create(
    model=model, max_tokens=max_tokens, system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": build_prompt(question, hits)}],
)
```

The response returns both the answer and the list of sources (file, title, score) so the UI can show where each `[n]` came from.

## 7. Step 5: Service Layer and Settings

> Keep business logic out of the web layer and configuration out of the code. `ChatbotService` owns the index, embedder and LLM client and exposes `ask()` and `reindex()`; `Settings` (pydantic-settings) validates every tunable value from `CHATBOT_*` env vars. Use it in any app you want to test, reuse from a CLI / MCP server, or configure per environment. Guide: [12 - Pydantic](12_pydantic.md) section 16.

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CHATBOT_", env_file=".env", extra="ignore")
    llm_model: str = "claude-opus-5"
    chunk_chars: int = Field(1200, gt=100)
    top_k: int = Field(4, ge=1, le=20)
    min_score: float = Field(0.05, ge=0, le=1)
```

```powershell
$env:CHATBOT_TOP_K = "6"          # change behaviour without touching code
```

## 8. Step 6: HTTP API with FastAPI and Uvicorn

> Serve the chatbot over HTTP with validation and docs. FastAPI routes validate input with Pydantic, call the service and return; the service is created once per worker in `lifespan`; Uvicorn runs the app. Use it for making any Python logic available to web apps, other services and UIs. Guides: [39 - FastAPI](39_fastapi.md), [40 - Uvicorn](40_uvicorn.md).

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = ChatbotService(Settings(), anthropic.Anthropic())
    yield

@app.post("/ask", response_model=Answer)
def ask(body: AskRequest, service: Service) -> Answer:
    return service.ask(body.question)
```

```bash
uv run uvicorn docs_chatbot.api:app --reload
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question": "Can I return a jacket?"}'
```

Open `http://127.0.0.1:8000/docs` to try `/ask`, `/reindex` and `/health` in the browser.

## 9. Step 7: Test Everything

> Automated tests for each layer, with no real API calls. A fake Claude response (`fake_text_message`), `tmp_path` for the index file, FastAPI's `TestClient` with `dependency_overrides` to inject a service with a fake client. Use it before every commit and in CI. Guide: [14 - pytest](14_pytest.md) sections 5, 11, 14.

```python
def test_service_answers_with_sources(settings):
    client = MagicMock()
    client.messages.create.return_value = fake_text_message("Jackets: 30 days if unworn [1].")
    answer = ChatbotService(settings, client).ask("How many days to return a jacket?")
    assert answer.sources[0].source == "refund-policy.md"
```

```bash
uv run pytest                 # 27 tests across all examples
uv run ruff check .
```

What is covered: chunk sizes and overlap, index search and save / load, prompt structure, "no hits skips the LLM", the service, all API routes including a 422 validation error.

## 10. Step 8: Measure Retrieval Quality

> A small eval set that checks whether the right document is retrieved for each question. `eval_data/retrieval.jsonl` holds questions and the expected source; `evals.py` computes recall@k and fails below 0.85. Use it after every change to chunking, embeddings or `top_k`. Guides: [34 - Evals](34_evals-observability.md), [30 - RAG](30_rag.md) section 17.

```bash
uv run python -m docs_chatbot.evals
# recall@4 = 1.00 over 8 cases
```

Add harder questions (paraphrases like "money back" instead of "refund") and watch the score drop with the hashing embedder; that is your signal to upgrade (section 16). Next level: an LLM-as-judge eval of answer faithfulness ([34](34_evals-observability.md) section 4).

## 11. Step 9: Containerise with Docker

> A production image that runs the API with Uvicorn. Slim Python base, uv installs from the lock file (cached layer), non-root user, exec-form `CMD` so Uvicorn receives stop signals. Use it before deploying anywhere. Guides: [42 - Docker](42_docker.md), [40 - Uvicorn](40_uvicorn.md) section 18.

```bash
cd examples
docker build -f docs_chatbot/Dockerfile -t docs-chatbot:1.0 .
docker run --rm -p 8000:8000 -e ANTHROPIC_API_KEY docs-chatbot:1.0
curl http://127.0.0.1:8000/health
```

`-e ANTHROPIC_API_KEY` (without a value) passes the key from your shell; it is never baked into the image.

## 12. Step 10: Automate with GitHub Actions

> CI that lints, tests, evaluates and builds the image on every push. `.github/workflows/examples.yml` runs `uv sync --locked`, Ruff, pytest, the retrieval eval and a Docker build; a second job tests against the newest library versions weekly to catch breaking changes early. Use it in every project in a Git repo. Guide: [43 - GitHub Actions](43_github-actions.md).

The weekly "latest dependencies" job is how this repo discovered that the MCP SDK v2 renamed `FastMCP`: automated tests notice API changes before readers do.

## 13. Step 11: Deploy to Azure Container Apps

> Run the container in the cloud with HTTPS and scale to zero. Build the image in Azure Container Registry, create a Container App with the API key as a secret. Use it for sharing the chatbot with real users. Guide: [47 - Azure](47_azure.md) sections 8, 9, 23.

```bash
RG=rg-docs-chatbot; LOC=swedencentral; ACR=acrdocsbot$RANDOM; APP=docs-chatbot
az group create -n $RG -l $LOC
az acr create -g $RG -n $ACR --sku Basic --admin-enabled true
cd examples && az acr build -r $ACR -t $APP:1.0 -f docs_chatbot/Dockerfile .

az containerapp env create -n cae-$APP -g $RG -l $LOC
az containerapp create -n $APP -g $RG --environment cae-$APP \
  --image $ACR.azurecr.io/$APP:1.0 --registry-server $ACR.azurecr.io \
  --target-port 8000 --ingress external --min-replicas 0 --max-replicas 2 \
  --secrets anthropic-key="$ANTHROPIC_API_KEY" --env-vars ANTHROPIC_API_KEY=secretref:anthropic-key

az containerapp show -n $APP -g $RG --query properties.configuration.ingress.fqdn -o tsv
az group delete -n $RG --yes --no-wait          # clean up when finished (stops all costs)
```

Before sharing publicly, add authentication and rate limiting ([37 - AI Security](37_ai-security.md) section 10, [41 - Redis](41_redis-queues.md) section 7).

## 14. Step 12: Add a Chat UI

> A web chat that calls your API. A small Streamlit app sends the question to `/ask` and shows the answer with its sources. Use it for demos and internal tools. Guide: [38 - AI UIs](38_ai-ui.md).

```python
# ui.py  ->  uv add streamlit httpx ; uv run streamlit run ui.py
import httpx
import streamlit as st

API_URL = "http://127.0.0.1:8000/ask"

st.title("Acme Help Chatbot")
if question := st.chat_input("Ask about refunds, shipping or your account"):
    st.chat_message("user").write(question)
    data = httpx.post(API_URL, json={"question": question}, timeout=60).json()
    with st.chat_message("assistant"):
        st.markdown(data["answer"])
        with st.expander("Sources"):
            for s in data["sources"]:
                st.markdown(f"[{s['id']}] **{s['source']}** (score {s['score']})")
```

## 15. Step 13: Expose It to AI Tools with MCP

> Let Claude Code, Claude Desktop or VS Code search the same documents. `examples/mcp_server/server.py` wraps the index as MCP tools (`search_docs`, `list_documents`) and a prompt. Use it for giving AI assistants access to your knowledge base. Guide: [33 - MCP](33_mcp.md).

```bash
cd examples
uv run mcp dev mcp_server/server.py                                   # try it in the Inspector
claude mcp add pocket-docs -- uv --directory "$(pwd)" run python -m mcp_server.server
```

## 16. Upgrade Path

> How to grow the capstone into a production-grade system. Replace one component at a time and re-run the tests and eval after each change. Use it when the basic version works and you want better quality, scale or safety.

| Upgrade | How | Guide |
|---|---|---|
| Semantic search | `SentenceTransformerEmbedder` (already in `embeddings.py`) or Ollama / Voyage embeddings | [29](29_embeddings-vector-db.md) |
| Better ranking | Retrieve 20, rerank with a cross-encoder to 5 | [30](30_rag.md) section 9 |
| Hybrid search | Combine vector scores with BM25 keyword search | [29](29_embeddings-vector-db.md) section 12 |
| Real vector database | Chroma, pgvector or Qdrant instead of NumPy | [29](29_embeddings-vector-db.md) sections 7-9 |
| PDFs and Word files | Add loaders (pypdf, docling) to `chunking.py` | [30](30_rag.md) section 2 |
| Streaming answers | `client.messages.stream` + `StreamingResponse` | [26](26_llm-apis.md) section 7, [38](38_ai-ui.md) section 10 |
| Lower cost | Prompt caching of the system prompt, cheaper model for simple questions | [26](26_llm-apis.md) section 11 |
| Answer quality evals | LLM-as-judge for faithfulness and citation accuracy | [34](34_evals-observability.md) |
| Agentic RAG | Give Claude a `search_docs` tool and let it search several times | [28](28_tool-use.md), [31](31_ai-agents.md) |
| Security | Auth, rate limits, per-user document permissions, prompt-injection tests | [37](37_ai-security.md) |
| Observability | Trace every request (Langfuse / OpenTelemetry), cost dashboards | [34](34_evals-observability.md) sections 12-15 |
| Background indexing | Re-index in a worker queue when documents change | [41](41_redis-queues.md) |
| Infrastructure as code | Terraform for the Azure resources | [46](46_terraform.md) section 14 |

## 17. What You Practised

| Skill | Where |
|---|---|
| Project setup, dependencies, lock files | Step 1 |
| Text processing and chunking | Step 2 |
| Embeddings and similarity search | Step 3 |
| Prompt design, grounding, citations, LLM API calls | Step 4 |
| Clean architecture, typed settings | Step 5 |
| REST API, validation, ASGI server | Step 6 |
| Testing with mocks and dependency overrides | Step 7 |
| Evaluation-driven development | Step 8 |
| Containers | Step 9 |
| CI/CD | Step 10 |
| Cloud deployment and secrets | Step 11 |
| UI prototyping | Step 12 |
| Tool integration standards (MCP) | Step 13 |

## 18. Troubleshooting

| Problem | Fix |
|---|---|
| `AuthenticationError` on `/ask` | `ANTHROPIC_API_KEY` not set in the shell / container; tests do not need it |
| Answer is always "I could not find that..." | No chunk passed `min_score`; lower `CHATBOT_MIN_SCORE`, rephrase, or upgrade to semantic embeddings |
| Old answers after editing documents | Call `POST /reindex` or delete `docs_chatbot/.index/` |
| `ModuleNotFoundError: docs_chatbot` | Run commands from the `examples/` folder with `uv run` |
| Port 8000 in use | `--port 8001` ([40](40_uvicorn.md) section 23) |
| Docker build cannot find `uv.lock` | Build from `examples/` with `-f docs_chatbot/Dockerfile .` |
| Container app shows 404 / no response | Target port must be 8000; check `az containerapp logs show -n $APP -g $RG` |
| Eval fails in CI after a change | Read the MISS lines: which questions lost their document? Fix chunking / embeddings, not the test |

---

<!-- nav:start -->
**Previous:** [48 - Azure VM + Linux + Ollama](48_azure-vm-ollama.md) | **Index:** [All guides](README.md) | **Next:** [98 - Glossary](98_glossary.md)
<!-- nav:end -->
