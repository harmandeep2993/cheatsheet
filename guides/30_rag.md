# 30 - RAG (Retrieval-Augmented Generation)

<!-- nav:start -->
**Previous:** [29 - Embeddings and Vector Databases](29_embeddings-vector-db.md) | **Index:** [All guides](../README.md) | **Next:** [31 - AI Agents](31_ai-agents.md)
<!-- nav:end -->

Quick reference for building RAG systems: loading documents, chunking, embedding, retrieval, reranking, prompting with citations, evaluating and improving answer quality.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is RAG?

**Retrieval-Augmented Generation** means: before the LLM answers, your app **retrieves** the most relevant pieces of your own documents and puts them into the prompt, so the model **generates** its answer from that material. It is how you build "chat with your documents", support bots that know your policies, and assistants over company knowledge, without retraining the model.

### Mental model: an open-book exam

An LLM on its own answers from memory (training data): it may not know your documents and may make things up. RAG turns it into an **open-book exam**: a librarian (the retriever) finds the right pages, and the student (the LLM) answers using those pages, citing them.

```text
=========================== INDEXING (offline, when documents change) ===========================

 PDFs, Word, web pages,   LOAD        CHUNK              EMBED               STORE
 Confluence, SQL rows  -> text  ->  ~300-800 token  ->  vector per    ->  vector DB
                                    pieces + metadata   chunk              (text + vector + metadata)

============================ QUERYING (online, for every question) =============================

 "What is our refund      EMBED       RETRIEVE           (RERANK)          GENERATE
  window for jackets?" -> query   ->  top 20 similar  ->  best 5 by a   ->  LLM prompt:
                          vector       chunks (+ filter)  reranker          instructions + chunks + question
                                                                              |
                                                                              v
                                                   "Jackets can be returned within 30 days [source: policy.pdf p.3]"
```

Two separate quality problems to keep in mind:

1. **Retrieval quality**: did we find the right chunks? (If not, the best LLM cannot answer.)
2. **Generation quality**: did the LLM use them correctly, completely and honestly?

### Why use RAG?

- **Your private / up-to-date knowledge** without fine-tuning.
- **Fewer hallucinations**: answers grounded in real sources, with citations users can check.
- **Easy updates**: change a document, re-index it; no retraining.
- **Access control**: retrieve only documents the user may see.
- **Cheaper than long context** for large knowledge bases (send 5 chunks, not 5,000 pages).

### Key terms

| Term | Meaning |
|---|---|
| Corpus / knowledge base | All documents you can retrieve from |
| Chunk | A piece of a document stored and retrieved as a unit |
| Chunk overlap | Repeated text between neighbouring chunks so ideas are not cut in half |
| Retriever | Component that finds relevant chunks for a query |
| Top-k | Number of chunks retrieved |
| Reranker | Model that re-scores retrieved chunks more precisely |
| Hybrid search | Vector + keyword search combined |
| Grounding / faithfulness | Answer supported by the retrieved text |
| Citation | Reference to the source of each claim |
| Agentic RAG | The LLM decides when and what to search, using a search tool |

**Where it fits:** built on [29 - Embeddings and Vector DBs](29_embeddings-vector-db.md), [26 - LLM APIs](26_llm-apis.md) and [27 - Prompt Engineering](27_prompt-engineering.md); agentic version with [28 - Tool Use](28_tool-use.md) / [31 - AI Agents](31_ai-agents.md); frameworks in [32](32_agent-frameworks.md); measured with [34 - Evals](34_evals-observability.md); served via [39 - FastAPI](39_fastapi.md) with a UI from [38](38_ai-ui.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Anthropic: contextual retrieval | https://www.anthropic.com/news/contextual-retrieval |
| Claude citations | https://platform.claude.com/docs/en/build-with-claude/citations |
| LlamaIndex | https://docs.llamaindex.ai/ |
| Ragas (RAG evaluation) | https://docs.ragas.io/ |
| Docling (document parsing) | https://docling-project.github.io/docling/ |
| pypdf | https://pypdf.readthedocs.io/ |

---

## Contents

1. [When to Use RAG (and When Not)](#1-when-to-use-rag-and-when-not)
2. [Loading Documents](#2-loading-documents)
3. [Cleaning Text](#3-cleaning-text)
4. [Chunking Strategies](#4-chunking-strategies)
5. [Chunking in Code](#5-chunking-in-code)
6. [Metadata](#6-metadata)
7. [Embedding and Indexing](#7-embedding-and-indexing)
8. [Retrieval](#8-retrieval)
9. [Reranking](#9-reranking)
10. [The Generation Prompt (with Citations)](#10-the-generation-prompt-with-citations)
11. [Complete Minimal RAG App](#11-complete-minimal-rag-app)
12. [Improving Retrieval](#12-improving-retrieval)
13. [Contextual Retrieval](#13-contextual-retrieval)
14. [Agentic RAG](#14-agentic-rag)
15. [Conversational RAG (Follow-up Questions)](#15-conversational-rag-follow-up-questions)
16. [Structured Data: Text-to-SQL](#16-structured-data-text-to-sql)
17. [Evaluating RAG](#17-evaluating-rag)
18. [Keeping the Index Fresh](#18-keeping-the-index-fresh)
19. [Security and Permissions](#19-security-and-permissions)
20. [RAG Frameworks](#20-rag-frameworks)
21. [Common Failures and Fixes](#21-common-failures-and-fixes)
22. [Try It](#22-try-it)

---

## 1. When to Use RAG (and When Not)

> Choosing between RAG, long context, fine-tuning and tools. Match the size and nature of the knowledge to the technique.
>
> Use it before building anything.

| Situation | Best approach |
|---|---|
| Few documents that fit easily in the context window | Put them all in the prompt (+ prompt caching) |
| Large or growing knowledge base (hundreds+ docs) | RAG |
| Data in databases / APIs (orders, metrics) | Tools / text-to-SQL, not embeddings |
| Need a specific style / format / narrow skill | Prompting, then fine-tuning ([36](36_fine-tuning.md)) |
| Frequently changing facts | RAG (re-index) or live tools |
| Open-ended research across sources | Agentic RAG ([31](31_ai-agents.md)) |

## 2. Loading Documents

> Getting plain text (and structure) out of files. Use a loader per file type; keep page numbers, headings and source paths as metadata.
>
> Use it at the start of the indexing pipeline.

```python
from pathlib import Path

from pypdf import PdfReader                    # pip install pypdf


def load_pdf(path: Path) -> list[dict]:
    """Return one record per page with text and metadata."""
    reader = PdfReader(path)
    return [
        {"text": page.extract_text() or "", "source": path.name, "page": i + 1}
        for i, page in enumerate(reader.pages)
    ]


def load_markdown(path: Path) -> list[dict]:
    return [{"text": path.read_text(encoding="utf-8"), "source": path.name, "page": None}]


records = []
for p in Path("docs").rglob("*"):
    if p.suffix == ".pdf":
        records += load_pdf(p)
    elif p.suffix in {".md", ".txt"}:
        records += load_markdown(p)
```

| File type | Libraries |
|---|---|
| PDF (text) | `pypdf`, `pymupdf` |
| PDF with tables / layout, scans | `docling`, `unstructured`, OCR (`pytesseract`), or send pages to a vision LLM |
| Word / PowerPoint | `python-docx`, `python-pptx`, `docling` |
| HTML / web | `trafilatura`, `beautifulsoup4` |
| Many formats | `unstructured`, `markitdown`, LlamaIndex / LangChain loaders |

## 3. Cleaning Text

> Removing noise that hurts retrieval. Normalise whitespace, drop headers / footers / page numbers, fix broken hyphenation, remove boilerplate.
>
> Use it after loading, before chunking.

```python
import re


def clean(text: str) -> str:
    text = re.sub(r"-\n(\w)", r"\1", text)           # join words hyphenated across lines
    text = re.sub(r"[ \t]+", " ", text)              # collapse spaces
    text = re.sub(r"\n{3,}", "\n\n", text)           # max one blank line
    text = re.sub(r"Page \d+ of \d+", "", text)      # page footers
    return text.strip()
```

Look at your extracted text before indexing; garbage in = garbage retrieved.

## 4. Chunking Strategies

> Splitting documents into retrievable pieces. Chunks should be big enough to contain a complete idea and small enough to be specific; overlap avoids cutting ideas in half.
>
> Use this when every RAG index. Chunking is one of the biggest quality levers.

| Strategy | How | Good for |
|---|---|---|
| Fixed size + overlap | Every N tokens / characters, overlap 10 to 20% | Simple baseline |
| Recursive / by separators | Split by paragraphs, then sentences, until under size | General text (default choice) |
| By structure | Split on Markdown / HTML headings, sections, pages | Manuals, docs, wikis |
| Semantic | Split where the topic changes (embedding similarity drops) | Long flowing text |
| Per record | One chunk per FAQ entry / ticket / product | Naturally separate items |
| Parent-child | Retrieve small chunks, send the larger parent section to the LLM | Precision + context |

Starting point: **300 to 800 tokens per chunk, 10 to 20% overlap**, split on paragraph / heading boundaries, and add the document title / section heading to each chunk. Then measure and tune.

## 5. Chunking in Code

> A simple, dependency-free recursive chunker. Split by paragraphs; merge paragraphs until the size limit; carry overlap into the next chunk.
>
> Use it for learning and small projects (frameworks have ready-made splitters).

```python
CHUNK_CHARS = 2000          # about 500 tokens of English
OVERLAP_CHARS = 300


def chunk_text(text: str, size: int = CHUNK_CHARS, overlap: int = OVERLAP_CHARS) -> list[str]:
    """Split text on paragraph boundaries into chunks of about `size` characters."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}" if current else para
            continue
        if current:
            chunks.append(current)
            current = current[-overlap:] + "\n\n" + para   # overlap keeps context across the boundary
        else:
            current = para
        while len(current) > size:                       # a single huge paragraph: hard split
            chunks.append(current[:size])
            current = current[size - overlap:]
    if current:
        chunks.append(current)
    return chunks
```

## 6. Metadata

> Extra fields stored with each chunk. Keep source, page, section, date, language, access level, a stable chunk ID.
>
> Use it for citations, filtering, permissions, updating / deleting documents.

```python
chunks = []
for rec in records:
    for i, piece in enumerate(chunk_text(clean(rec["text"]))):
        chunks.append({
            "id": f"{rec['source']}::p{rec['page']}::c{i}",   # stable ID -> easy updates
            "text": piece,
            "source": rec["source"],
            "page": rec["page"],
            "tenant_id": "acme",
        })
```

## 7. Embedding and Indexing

> Turning chunks into vectors and storing them. Batch-embed chunk texts; store id, text, vector and metadata in a vector store.
>
> Use it for initial build and whenever documents change.

```python
import chromadb
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("BAAI/bge-m3")                        # multilingual, strong
db = chromadb.PersistentClient(path="./rag_db")
col = db.get_or_create_collection("kb", metadata={"hnsw:space": "cosine"})

BATCH = 64
for start in range(0, len(chunks), BATCH):
    batch = chunks[start:start + BATCH]
    col.upsert(
        ids=[c["id"] for c in batch],
        documents=[c["text"] for c in batch],
        embeddings=embedder.encode([c["text"] for c in batch], normalize_embeddings=True).tolist(),
        metadatas=[{k: v for k, v in c.items() if k not in ("id", "text") and v is not None} for c in batch],
    )
```

## 8. Retrieval

> Finding the chunks most relevant to the question. Embed the query with the same model, search top-k with filters; optionally combine with keyword search.
>
> Use it in every question.

```python
TOP_K = 20


def retrieve(question: str, tenant_id: str, k: int = TOP_K) -> list[dict]:
    q_vec = embedder.encode(question, normalize_embeddings=True).tolist()
    res = col.query(query_embeddings=[q_vec], n_results=k, where={"tenant_id": tenant_id})
    return [
        {"text": doc, "source": meta["source"], "page": meta.get("page"), "distance": dist}
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]
```

Typical settings: retrieve 10 to 30 candidates, then rerank down to 3 to 8 for the prompt.

## 9. Reranking

> A second, more accurate scoring of retrieved chunks. A cross-encoder reads the question and each chunk **together** and scores relevance (slower than embeddings, so only on the top candidates).
>
> It is almost always worth it once basic RAG works; big quality gain for little code.

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")
FINAL_K = 5


def rerank(question: str, candidates: list[dict], k: int = FINAL_K) -> list[dict]:
    scores = reranker.predict([(question, c["text"]) for c in candidates])
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [c for c, _ in ranked[:k]]
```

Hosted rerankers exist too (Cohere, Voyage, Azure AI Search semantic ranker).

## 10. The Generation Prompt (with Citations)

> Asking the LLM to answer from the retrieved chunks only, and cite them. Put numbered, tagged sources first, the question last, rules for citations and for missing information.
>
> Use it in every RAG answer.

```python
RAG_SYSTEM = (
    "You answer questions for Acme employees using only the provided sources. "
    "Cite sources after each claim like [1] or [2][3]. "
    "If the sources do not contain the answer, say you could not find it in the documentation "
    "and suggest who to ask. Do not use outside knowledge."
)


def build_prompt(question: str, chunks: list[dict]) -> str:
    sources = "\n".join(
        f'<source id="{i}" file="{c["source"]}" page="{c["page"]}">\n{c["text"]}\n</source>'
        for i, c in enumerate(chunks, start=1)
    )
    return f"<sources>\n{sources}\n</sources>\n\nQuestion: {question}"
```

Provider features like Claude's **citations** on document blocks can return exact cited spans automatically ([26](26_llm-apis.md)).

## 11. Complete Minimal RAG App

> All steps together in one small program. Retrieve -> rerank -> prompt -> Claude answer with sources.
>
> Use it as a template for your first RAG project.

```python
import anthropic

client = anthropic.Anthropic()


def answer(question: str, tenant_id: str = "acme") -> dict:
    """Answer a question from the knowledge base with citations."""
    candidates = retrieve(question, tenant_id)
    if not candidates:
        return {"answer": "No documents found.", "sources": []}
    top = rerank(question, candidates)
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=16000,
        system=RAG_SYSTEM,
        messages=[{"role": "user", "content": build_prompt(question, top)}],
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    return {"answer": text, "sources": [{"id": i, "file": c["source"], "page": c["page"]}
                                         for i, c in enumerate(top, start=1)]}


print(answer("How many days do customers have to return a jacket?"))
```

Serve it with FastAPI ([39](39_fastapi.md)) and a chat UI ([38](38_ai-ui.md)).

## 12. Improving Retrieval

> Techniques to find better chunks. Change the query, the index or the ranking; measure each change.
>
> Use it when the right answer exists in the docs but is not retrieved.

| Technique | How | Helps when |
|---|---|---|
| Hybrid search | Vector + BM25 keyword search, merged | Exact codes, names, jargon |
| Reranking | Cross-encoder on top-k | Right chunk retrieved but ranked low |
| Better chunking | Structure-aware, right size, headings in chunks | Answers split across chunks |
| Query rewriting | LLM rewrites the question into a clear search query | Vague / conversational questions |
| Multi-query | LLM generates 3 to 5 query variants, merge results | Different wording in docs |
| HyDE | Embed a hypothetical answer instead of the question | Short questions, long documents |
| Metadata filters | Date / product / language filters | Too many near-duplicate docs |
| Parent-child | Retrieve small, send larger surrounding section | Precise match but missing context |
| Better embedding model | Stronger or domain / multilingual model | Generally poor matches |

## 13. Contextual Retrieval

> Adding a short explanation of each chunk's context before embedding it. For each chunk, an LLM writes 1 to 2 sentences situating it in the whole document ("This section of the 2025 refund policy covers jackets..."); prepend that to the chunk text for embedding and keyword indexing.
>
> Use it for chunks that are ambiguous on their own ("It must be returned within 30 days" - what is "it"?). Use prompt caching on the full document to keep the cost low.

```python
CONTEXT_PROMPT = """<document>
{document}
</document>
Here is a chunk from the document:
<chunk>
{chunk}
</chunk>
Write 1-2 sentences that situate this chunk within the overall document to improve search retrieval.
Answer only with the context."""
```

## 14. Agentic RAG

> Letting the LLM decide when and what to search, possibly several times. Expose retrieval as a tool (`search_docs(query, filters)`); the model searches, reads results, refines the query, and answers when it has enough ([28](28_tool-use.md), [31](31_ai-agents.md)).
>
> Use it for complex questions needing several lookups or comparisons; mixed sources (docs + DB + web).

```text
User: "Compare our 2024 and 2025 refund policies for electronics."
Agent: search_docs("refund policy electronics 2024")   -> chunks A
       search_docs("refund policy electronics 2025")   -> chunks B
       answer comparing A and B with citations
```

Trade-offs: better on hard questions, but slower, costlier and less predictable than a fixed pipeline.

## 15. Conversational RAG (Follow-up Questions)

> Handling questions that depend on earlier turns ("and what about shoes?"). Before retrieval, rewrite the latest question into a standalone query using the chat history.
>
> Use it in every chat-style RAG app.

```python
REWRITE_PROMPT = """Given the conversation and the follow-up question, rewrite the follow-up
as a standalone search query. Reply with the query only.

<conversation>
{history}
</conversation>
Follow-up: {question}"""
```

## 16. Structured Data: Text-to-SQL

> Answering questions about tables by generating SQL instead of embedding rows. Give the LLM the schema; it writes a query; your code runs it with a read-only user; the LLM explains the result.
>
> Use it for numbers, aggregates, filters over databases ("revenue by region last quarter"). Embeddings are bad at arithmetic over rows.

Safety: read-only DB user, allow-listed tables, row limits, statement timeouts, validate / parse the SQL before running. See [19 - SQL](19_sql.md).

## 17. Evaluating RAG

> Measuring retrieval and answer quality separately. Build a test set of questions with expected answers and the source chunks that contain them; score each stage.
>
> Use it before launch, and after every change to chunking, models or prompts.

| Stage | Metric | Question it answers |
|---|---|---|
| Retrieval | Recall@k / hit rate | Is the right chunk in the top k? |
| Retrieval | MRR | How high is the first right chunk? |
| Generation | Faithfulness / groundedness | Is every claim supported by the sources? |
| Generation | Answer relevance / correctness | Does it answer the question correctly and completely? |
| Generation | Citation accuracy | Do citations point to the right source? |
| End to end | "Don't know" accuracy | Does it refuse when the answer is not in the docs? |

```python
def recall_at_k(test_set: list[dict], k: int = 5) -> float:
    """Share of questions where an expected chunk id appears in the top k results."""
    hits = 0
    for case in test_set:
        ids = [c["id"] for c in retrieve_with_ids(case["question"], k=k)]
        hits += any(e in ids for e in case["expected_chunk_ids"])
    return hits / len(test_set)
```

Generation quality is often graded with an LLM-as-judge and a rubric. Tools: Ragas, DeepEval, promptfoo, Langfuse ([34](34_evals-observability.md)).

## 18. Keeping the Index Fresh

> Updating the index when documents change. Stable chunk IDs, content hashes to detect changes, upsert changed chunks, delete removed ones.
>
> Use it in any living knowledge base.

- Store a hash of each document; re-process only changed files.
- Delete all chunks of a document (by `source` metadata) before re-adding its new version.
- Schedule re-indexing (cron / GitHub Actions / queue workers, [41](41_redis-queues.md), [43](43_github-actions.md)).
- Record the embedding model version; re-embed everything when it changes.

## 19. Security and Permissions

> Making sure users only get answers from documents they may see, and that documents cannot hijack the model. Filter by user permissions at retrieval; treat retrieved text as untrusted data.
>
> Use it in any multi-user or internal-document RAG.

- Store access metadata (tenant, team, role) with every chunk; filter on **every** query in code.
- Retrieved documents can contain prompt-injection text ("ignore previous instructions..."); tag them as data and do not give the RAG model risky tools ([37](37_ai-security.md)).
- Remove secrets and personal data before indexing where possible.
- Log questions and sources for auditing (respect privacy rules).

## 20. RAG Frameworks

> Libraries that provide loaders, splitters, retrievers and pipelines. They wrap the steps above; you trade control for speed of setup.
>
> Use it for many file types, complex pipelines, or quick prototypes. Plain code is often clearer for small apps.

| Framework | Strength |
|---|---|
| LlamaIndex | Data loading, indexing and retrieval for RAG |
| LangChain / LangGraph | Broad integrations, chains and agent graphs |
| Haystack | Production search / RAG pipelines |
| Azure AI Search + Azure OpenAI "on your data" | Managed RAG on Azure |

More in [32 - Agent Frameworks](32_agent-frameworks.md).

## 21. Common Failures and Fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| "I couldn't find it" but the doc has it | Retrieval miss | Check recall; hybrid search; better chunking; rewrite queries |
| Answer uses the wrong document | Similar docs / versions | Metadata filters (date, product); reranking |
| Answer is partial | Info spread across chunks | Bigger chunks / parent-child; retrieve more; agentic multi-search |
| Hallucinated details | Weak grounding instructions or poor chunks | "Only use sources", allow "don't know", require citations, faithfulness evals |
| Tables / numbers garbled | PDF extraction | Layout-aware loaders (docling) or vision model on pages |
| Slow responses | Too many / large chunks, slow reranker | Fewer chunks, smaller reranker, cache, stream the answer |
| Costs high | Huge prompts | Fewer chunks, prompt caching of stable parts, smaller model for rewriting |
| Works in tests, fails for users | Test questions unlike real ones | Build eval set from real user questions |
| Follow-up questions fail | No query rewriting | Conversational rewrite step (section 15) |

## 22. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Run the retrieval eval

In `examples/`, run the retrieval eval, then add a question phrased with different words ("When do I get my money back?") and run it again.

<details markdown="1">
<summary>Solution</summary>

```bash
cd examples
uv run python -m docs_chatbot.evals
```

The paraphrase fails with the offline hashing embedder (it matches spelling, not meaning). Switching to `SentenceTransformerEmbedder` fixes it: that is exactly why real RAG uses semantic embeddings.

</details>

### Exercise 2: System prompt

Write a RAG system prompt that requires citations and defines what to say when the answer is missing.

<details markdown="1">
<summary>Solution</summary>

See `SYSTEM_PROMPT` in `examples/docs_chatbot/answer.py`: answer only from numbered sources, cite `[n]` after each claim, reply with an exact fallback sentence when the sources do not contain the answer, no outside knowledge.

</details>

### Exercise 3: Debug a wrong answer

The document contains the answer but the bot says it cannot find it. What do you check, in order?

<details markdown="1">
<summary>Solution</summary>

1. Retrieval: is the right chunk in the top-k (print hits and scores)? 2. Chunking: is the answer split across chunks? 3. Wording: add hybrid search or query rewriting. 4. Thresholds: `min_score` too high? 5. Only then the prompt / model.

</details>

---

<!-- nav:start -->
**Previous:** [29 - Embeddings and Vector Databases](29_embeddings-vector-db.md) | **Index:** [All guides](../README.md) | **Next:** [31 - AI Agents](31_ai-agents.md)
<!-- nav:end -->
