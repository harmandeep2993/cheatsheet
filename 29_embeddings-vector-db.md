# 29 - Embeddings and Vector Databases

<!-- nav:start -->
**Previous:** [28 - Tool Use (Function Calling)](28_tool-use.md) | **Index:** [All guides](README.md) | **Next:** [30 - RAG (Retrieval-Augmented Generation)](30_rag.md)
<!-- nav:end -->

Quick reference for turning text into vectors (embeddings), measuring similarity, and storing / searching vectors with NumPy, FAISS, Chroma, pgvector, Qdrant and Azure AI Search.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What are embeddings and vector databases?

An **embedding** is a list of numbers (a **vector**, e.g. 384 or 1024 numbers) that represents the **meaning** of a piece of text (or an image). An **embedding model** is trained so that texts with similar meaning get vectors that are close together, even when they share no words ("car" and "automobile"). A **vector database** stores millions of these vectors and quickly finds the ones closest to a query vector. Together they power **semantic search**, **RAG**, recommendations, clustering and duplicate detection.

### Mental model: a map of meaning

```text
                      ^  dimension 2
                      |
        "reset password" *  * "forgot my login"          <- close: similar meaning
                      |   * "can't sign in"
                      |
   ---------------------------------------------------->  dimension 1
                      |
                      |            * "shipping takes 3 days"
                      |          * "delivery time"         <- another cluster
                      |

Real embeddings have hundreds of dimensions, but the idea is the same:
search = embed the question -> find the nearest points on the map.
```

```text
INDEXING (once / when data changes)             SEARCHING (every query)
documents -> chunks -> embedding model          question -> embedding model -> query vector
          -> vectors + text + metadata                   -> vector DB: nearest k vectors
          -> vector database                             -> matching chunks (+ scores)
```

Keyword search (`LIKE '%password%'`) finds exact words; **semantic search** finds meaning. Combining both (**hybrid search**) is often best.

### Why use them?

- **Search by meaning** in documents, tickets, products, code.
- **RAG**: find the right context to give an LLM ([30 - RAG](30_rag.md)).
- **Cheap and fast**: embedding models are much smaller and cheaper than chat LLMs.
- **Other uses**: clustering, deduplication, recommendations, classification features, anomaly detection.

### Key terms

| Term | Meaning |
|---|---|
| Embedding / vector | List of floats representing meaning |
| Dimension | Length of the vector (384, 768, 1024, 1536, 3072 ...) |
| Embedding model | Model that converts text to vectors |
| Cosine similarity | Similarity of direction between two vectors (-1 to 1; higher = more similar) |
| Distance | Opposite of similarity (smaller = closer) |
| Nearest neighbours (kNN) | The k most similar vectors |
| ANN | Approximate nearest neighbour: fast, slightly inexact search |
| HNSW | Popular graph-based ANN index |
| Collection / index | A named set of vectors in a vector DB |
| Metadata / payload | Extra fields stored with each vector (source, date, user) for filtering |
| Hybrid search | Combining vector similarity with keyword (BM25) search |
| Normalisation | Scaling vectors to length 1 (then dot product = cosine) |

**Where it fits:** concept in [25 - LLM Fundamentals](25_llm-fundamentals.md); models from [24 - Hugging Face](24_hugging-face.md) or Ollama ([35](35_local-llms.md)); used by [30 - RAG](30_rag.md) and agents' memory ([31](31_ai-agents.md)); pgvector builds on [19 - SQL](19_sql.md); databases run in [42 - Docker](42_docker.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Sentence Transformers | https://sbert.net/ |
| MTEB embedding leaderboard | https://huggingface.co/spaces/mteb/leaderboard |
| OpenAI embeddings guide | https://platform.openai.com/docs/guides/embeddings |
| Voyage AI docs | https://docs.voyageai.com/ |
| Chroma | https://docs.trychroma.com/ |
| pgvector | https://github.com/pgvector/pgvector |
| Qdrant | https://qdrant.tech/documentation/ |
| FAISS | https://github.com/facebookresearch/faiss/wiki |
| Azure AI Search | https://learn.microsoft.com/en-us/azure/search/ |

---

## Contents

1. [Creating Embeddings](#1-creating-embeddings)
2. [Choosing an Embedding Model](#2-choosing-an-embedding-model)
3. [Similarity Metrics](#3-similarity-metrics)
4. [Brute-Force Search with NumPy](#4-brute-force-search-with-numpy)
5. [How Vector Indexes Work (ANN, HNSW)](#5-how-vector-indexes-work-ann-hnsw)
6. [FAISS (In-Memory Library)](#6-faiss-in-memory-library)
7. [Chroma (Local Vector DB)](#7-chroma-local-vector-db)
8. [pgvector (PostgreSQL)](#8-pgvector-postgresql)
9. [Qdrant (Vector DB Server)](#9-qdrant-vector-db-server)
10. [Azure AI Search and Other Managed Options](#10-azure-ai-search-and-other-managed-options)
11. [Metadata Filtering](#11-metadata-filtering)
12. [Hybrid Search (Vector + Keyword)](#12-hybrid-search-vector--keyword)
13. [Other Uses: Clustering, Dedup, Classification](#13-other-uses-clustering-dedup-classification)
14. [Which Vector Store When](#14-which-vector-store-when)
15. [Performance and Cost Tips](#15-performance-and-cost-tips)
16. [Troubleshooting](#16-troubleshooting)
17. [Try It](#17-try-it)

---

## 1. Creating Embeddings

> Converting text into vectors with an embedding model. Local models (sentence-transformers, Ollama) or hosted APIs (OpenAI, Voyage, Azure OpenAI, Cohere); send a list of texts, get a list of vectors. Use it for indexing documents and embedding each search query with the SAME model.

```python
# Local, free: sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
vectors = model.encode(["How do I reset my password?", "Shipping takes 3 days"],
                       normalize_embeddings=True)          # numpy array, shape (2, 384)
```

```python
# Local via Ollama (ollama pull bge-m3)
import ollama

resp = ollama.embed(model="bge-m3", input=["How do I reset my password?"])
vectors = resp["embeddings"]                                # list of lists (1024 dims)
```

```python
# Hosted: OpenAI
from openai import OpenAI

client = OpenAI()
resp = client.embeddings.create(model="text-embedding-3-small", input=["How do I reset my password?"])
vectors = [d.embedding for d in resp.data]                  # 1536 dims
```

Anthropic does not offer its own embedding model; Voyage AI models are a common pairing with Claude (`pip install voyageai`), with an `input_type` of `"document"` for indexing and `"query"` for searches.

## 2. Choosing an Embedding Model

> Picking the model that turns your text into vectors. Balance quality, language support, dimension (storage), speed, cost and privacy. Check the MTEB leaderboard on Hugging Face for rankings. Use it before indexing; changing the model later means re-embedding everything.

| Model (examples) | Where | Dims | Notes |
|---|---|---|---|
| `all-MiniLM-L6-v2` | Local (sentence-transformers) | 384 | Tiny, fast, English, great for learning |
| `bge-m3` | Local (HF / Ollama) | 1024 | Multilingual, long inputs, strong |
| `multilingual-e5-large` | Local (HF) | 1024 | Multilingual (needs "query: " / "passage: " prefixes) |
| `nomic-embed-text` | Ollama | 768 | Good local default |
| `text-embedding-3-small` / `-large` | OpenAI / Azure OpenAI | 1536 / 3072 | Easy hosted option; can shorten dimensions |
| Voyage models | Voyage API | varies | Strong retrieval quality, domain variants (code, finance, law) |

Rules:

- **Same model for documents and queries.** Vectors from different models are not comparable.
- Store the model name with your index so you know when to re-embed.
- Multilingual data -> multilingual model.

## 3. Similarity Metrics

> How "closeness" between two vectors is measured. Cosine similarity compares direction; dot product equals cosine for normalised vectors; Euclidean measures straight-line distance. Use it for configuring a vector DB; use what the embedding model recommends (usually cosine).

| Metric | Formula idea | Range | Use |
|---|---|---|---|
| Cosine similarity | angle between vectors | -1 to 1 (higher = closer) | Default for text embeddings |
| Dot product | sum of a[i] * b[i] | any | Same as cosine if normalised; fastest |
| Euclidean (L2) distance | straight-line distance | 0 to inf (lower = closer) | Some models / image embeddings |

```python
import numpy as np

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
```

Similarity scores are **relative**: 0.8 might be "very similar" for one model and "average" for another. Compare scores within the same model, and choose thresholds from your own data.

## 4. Brute-Force Search with NumPy

> Searching by comparing the query to every stored vector. One matrix multiplication with normalised vectors gives all cosine scores; take the top k. Use it for up to tens of thousands of chunks, prototypes, tests. Exact and dependency-free.

```python
import numpy as np

docs = ["How do I reset my password?", "Shipping takes 3 days", "Forgot my login details"]
doc_vecs = model.encode(docs, normalize_embeddings=True)           # (n_docs, dim)


def search(query: str, k: int = 2) -> list[tuple[str, float]]:
    q = model.encode(query, normalize_embeddings=True)             # (dim,)
    scores = doc_vecs @ q                                          # cosine for normalised vectors
    top = np.argsort(-scores)[:k]
    return [(docs[i], float(scores[i])) for i in top]


search("I can't log in")      # [('Forgot my login details', 0.71), ('How do I reset my password?', 0.55)]

np.save("doc_vecs.npy", doc_vecs)                                   # persist
```

## 5. How Vector Indexes Work (ANN, HNSW)

> Data structures that find near vectors without checking every one. HNSW builds a multi-layer graph linking each vector to its neighbours; search walks the graph from coarse to fine. Results are approximate but very fast. Use it for hundreds of thousands to billions of vectors, low latency needs.

```text
Layer 2 (few nodes, long jumps)      A ----------------------- F
Layer 1                              A ------- C ------- F --- H
Layer 0 (all nodes, short links)     A - B - C - D - E - F - G - H - I
Search: start at the top, jump toward the query, go down a layer, refine, repeat.
```

| Setting (HNSW) | Higher value means |
|---|---|
| `M` | More links per node: better recall, more memory |
| `ef_construction` | Better index quality, slower build |
| `ef` / `ef_search` | Better recall at query time, slower search |

**Recall** = share of the true nearest neighbours that the ANN search actually returns.

## 6. FAISS (In-Memory Library)

> Meta's library for fast vector search in memory (CPU / GPU). Build an index object, add vectors, search; save / load the index as a file. Stores vectors only (keep text / metadata in your own list or DB). Use it for fast local search inside one Python process; research; large static datasets.

```python
import faiss                             # pip install faiss-cpu
import numpy as np

dim = doc_vecs.shape[1]
index = faiss.IndexFlatIP(dim)           # exact inner product (= cosine with normalised vectors)
index.add(doc_vecs.astype(np.float32))

q = model.encode(["I can't log in"], normalize_embeddings=True).astype(np.float32)
scores, ids = index.search(q, 3)         # top 3
[docs[i] for i in ids[0]]

faiss.write_index(index, "docs.faiss")
index = faiss.read_index("docs.faiss")
hnsw = faiss.IndexHNSWFlat(dim, 32)      # approximate, faster for big data
```

## 7. Chroma (Local Vector DB)

> An easy, open-source vector database that runs inside Python (or as a server). Collections store ids, documents, metadata and embeddings; Chroma can embed text for you with a default or custom embedding function. Use it for prototypes, small / medium RAG apps, notebooks, local tools.

```python
import chromadb                          # pip install chromadb

client = chromadb.PersistentClient(path="./chroma_db")          # saved to disk
col = client.get_or_create_collection("support_docs", metadata={"hnsw:space": "cosine"})

col.add(
    ids=["doc1", "doc2", "doc3"],
    documents=["How do I reset my password?", "Shipping takes 3 days", "Forgot my login details"],
    metadatas=[{"topic": "account"}, {"topic": "shipping"}, {"topic": "account"}],
)                                        # uses Chroma's default embedding model

res = col.query(query_texts=["I can't log in"], n_results=2, where={"topic": "account"})
res["documents"][0], res["distances"][0], res["metadatas"][0]

col.upsert(ids=["doc2"], documents=["Shipping takes 2 to 4 days"], metadatas=[{"topic": "shipping"}])
col.delete(ids=["doc3"])
col.count()
```

To use your own model, pass `embeddings=` in `add` / `query_embeddings=` in `query`, or set an `embedding_function` on the collection.

## 8. pgvector (PostgreSQL)

> A PostgreSQL extension that adds a `vector` column type and similarity search. Store embeddings next to your normal data; query with distance operators in SQL; add an HNSW index for speed. Use this when you already use Postgres; you want vectors, metadata, permissions and transactions in one database.

```bash
docker run -d --name pgvec -e POSTGRES_PASSWORD=pass -p 5432:5432 pgvector/pgvector:pg16
```

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE chunks (
    id        BIGSERIAL PRIMARY KEY,
    source    TEXT,
    content   TEXT,
    embedding VECTOR(384)                  -- must match your model's dimension
);

CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

-- 5 most similar chunks (<=> cosine distance, <-> L2, <#> negative inner product)
SELECT source, content, 1 - (embedding <=> '[0.1, 0.2, ...]') AS similarity
FROM chunks
WHERE source LIKE 'handbook%'
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 5;
```

```python
import numpy as np
import psycopg                                   # pip install "psycopg[binary]" pgvector
from pgvector.psycopg import register_vector

conn = psycopg.connect("postgresql://postgres:pass@localhost:5432/postgres", autocommit=True)
register_vector(conn)

conn.execute("INSERT INTO chunks (source, content, embedding) VALUES (%s, %s, %s)",
             ("faq.md", text, np.array(vec)))
rows = conn.execute(
    "SELECT content, 1 - (embedding <=> %s) AS sim FROM chunks ORDER BY embedding <=> %s LIMIT 5",
    (np.array(qvec), np.array(qvec)),
).fetchall()
```

Available as a managed option on Azure Database for PostgreSQL ([47 - Azure](47_azure.md)).

## 9. Qdrant (Vector DB Server)

> A fast, open-source vector database server with rich filtering. Runs as a service (Docker or cloud); Python client creates collections, upserts points (vector + payload) and queries. Use it for production RAG with large collections, heavy filtering, multiple apps sharing one store.

```bash
docker run -d -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

```python
from qdrant_client import QdrantClient, models      # pip install qdrant-client

client = QdrantClient(url="http://localhost:6333")    # or QdrantClient(":memory:") for tests
client.create_collection(
    "docs",
    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
)
client.upsert("docs", points=[
    models.PointStruct(id=i, vector=v.tolist(), payload={"text": t, "topic": topic})
    for i, (v, t, topic) in enumerate(zip(doc_vecs, docs, topics))
])

hits = client.query_points(
    "docs",
    query=model.encode("I can't log in").tolist(),
    limit=3,
    query_filter=models.Filter(must=[models.FieldCondition(key="topic", match=models.MatchValue(value="account"))]),
).points
[(h.payload["text"], h.score) for h in hits]
```

## 10. Azure AI Search and Other Managed Options

> Hosted search services that combine vector, keyword and filter search. You push documents (with vectors or let the service vectorise them); query through an API; the provider handles scaling and backups. Use it for enterprise apps, large data, when you do not want to run a database yourself.

| Service | Notes |
|---|---|
| Azure AI Search | Hybrid (vector + BM25) + semantic ranker, integrates with Azure OpenAI and Blob Storage ([47](47_azure.md)) |
| Pinecone | Fully managed, serverless vector DB |
| Qdrant Cloud, Weaviate Cloud, Zilliz (Milvus) | Managed versions of open-source DBs |
| Elasticsearch / OpenSearch | Mature keyword search with vector support |
| MongoDB Atlas Vector Search, Cosmos DB | Vectors inside document databases |

## 11. Metadata Filtering

> Restricting a vector search by structured fields. Store fields (source, date, language, customer, access level) with each vector; filter before / during the similarity search. Use it for multi-tenant apps (users only see their documents), time ranges, document types, permissions.

```python
col.query(query_texts=[q], n_results=5, where={"$and": [{"tenant_id": "acme"}, {"year": {"$gte": 2025}}]})
```

Security rule: enforce access filters in your code on every query; never rely on the LLM to hide documents it should not see.

## 12. Hybrid Search (Vector + Keyword)

> Combining semantic similarity with classic keyword matching. Run both searches, then merge the rankings (for example Reciprocal Rank Fusion). Use it for queries with exact terms (product codes, names, error messages) where pure vector search misses matches.

```python
from rank_bm25 import BM25Okapi       # pip install rank-bm25

bm25 = BM25Okapi([d.lower().split() for d in docs])
keyword_scores = bm25.get_scores("error E-4012".lower().split())

RRF_K = 60                             # damping constant commonly used for Reciprocal Rank Fusion


def rrf(rankings: list[list[int]]) -> list[int]:
    """Merge several ranked lists of doc ids; items ranked high in any list rise to the top."""
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (RRF_K + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)
```

Many vector DBs (Qdrant, Weaviate, Azure AI Search, Elasticsearch) have hybrid search built in.

## 13. Other Uses: Clustering, Dedup, Classification

> Using embeddings beyond search. Treat vectors as features for classic ML ([22 - Scikit-learn](22_scikit-learn.md)). Use it for grouping feedback, finding duplicates, cheap classifiers.

```python
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression

labels = KMeans(n_clusters=8, n_init="auto", random_state=42).fit_predict(vectors)   # topic clusters

DUPLICATE_THRESHOLD = 0.95                               # tune on your own data
sim = vectors @ vectors.T
dupes = [(i, j) for i in range(len(sim)) for j in range(i + 1, len(sim)) if sim[i, j] > DUPLICATE_THRESHOLD]

clf = LogisticRegression(max_iter=1000).fit(train_vectors, train_labels)   # fast text classifier
```

## 14. Which Vector Store When

> Picking storage for your vectors. Start simple; move up when size, concurrency or features demand it. Use it for designing a RAG / search system.

| Situation | Choose |
|---|---|
| Learning, < 50k chunks, one script | NumPy / FAISS |
| Prototype RAG app with persistence | Chroma |
| Already on Postgres, want SQL + vectors | pgvector |
| Large scale, heavy filtering, dedicated service | Qdrant / Weaviate / Milvus |
| Enterprise on Azure, hybrid + semantic ranking | Azure AI Search |
| No-ops managed service | Pinecone, Qdrant Cloud |

## 15. Performance and Cost Tips

> Keeping indexing and search fast and cheap. Batch embedding calls, cache vectors, choose dimensions wisely. Use it for indexing large corpora, production search.

- Embed in **batches** (e.g. 64 to 256 texts per call) instead of one by one.
- **Cache** embeddings (hash of text -> vector); never re-embed unchanged text.
- Smaller dimensions = less storage and faster search (some models let you truncate).
- Store vectors as `float32` (or quantized in the DB) rather than float64.
- Re-embed everything when you change the embedding model; version your index.

## 16. Troubleshooting

| Problem | Fix |
|---|---|
| `dimension mismatch` / `expected 1024 dimensions, got 384` | Collection / column created for another model; recreate with the right size |
| Results look random | Different models for docs vs queries; missing normalisation; wrong metric |
| Exact terms (codes, names) not found | Add hybrid keyword search |
| Good matches ranked low | Chunks too big / too small ([30](30_rag.md)); add a reranker; try a stronger model |
| Slow search with many vectors | Use an ANN index (HNSW); raise hardware; filter first |
| Scores all around 0.8 | Normal for some models; compare relative ranking, tune thresholds on your data |
| `faiss` install fails on Windows | `pip install faiss-cpu` (or use Chroma / Qdrant) |
| Users see other users' docs | Enforce metadata filters (tenant / permissions) in code on every query |
| Chroma / DB lost data on restart | Use `PersistentClient(path=...)` / Docker volumes |

## 17. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution. Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Cosine by hand

Embed three sentences and print the similarity matrix.

<details markdown="1">
<summary>Solution</summary>

```python
emb = model.encode(sentences, normalize_embeddings=True)
emb @ emb.T          # cosine similarity for normalised vectors
```

</details>

### Exercise 2: Chroma with a filter

Add three documents with a `topic` metadata field and query only the `account` topic.

<details markdown="1">
<summary>Solution</summary>

```python
col = chromadb.PersistentClient("./db").get_or_create_collection("kb", metadata={"hnsw:space": "cosine"})
col.add(ids=["1", "2", "3"], documents=docs, metadatas=[{"topic": "account"}, {"topic": "shipping"}, {"topic": "account"}])
col.query(query_texts=["can't log in"], n_results=2, where={"topic": "account"})
```

</details>

### Exercise 3: Same model rule

Why must documents and queries use the same embedding model?

<details markdown="1">
<summary>Solution</summary>

Each model has its own vector space: dimensions and meaning differ, so distances between vectors from two different models are meaningless. Changing the model means re-embedding everything.

</details>

---

<!-- nav:start -->
**Previous:** [28 - Tool Use (Function Calling)](28_tool-use.md) | **Index:** [All guides](README.md) | **Next:** [30 - RAG (Retrieval-Augmented Generation)](30_rag.md)
<!-- nav:end -->
