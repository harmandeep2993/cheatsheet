# 41 - Redis, Caching and Task Queues

<!-- nav:start -->
**Previous:** [40 - Uvicorn (ASGI Server)](40_uvicorn.md) | **Index:** [All guides](README.md) | **Next:** [42 - Docker](42_docker.md)
<!-- nav:end -->

Quick reference for Redis (in-memory data store) and background job queues: caching LLM responses, rate limiting, sessions, pub/sub, and running slow work with Celery, RQ or arq.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What are Redis and task queues?

- **Redis** is an extremely fast **in-memory key-value store**. Programs save and read small pieces of data in microseconds: cached results, counters, sessions, queues. It runs as a separate server (often in Docker) that many app processes share.
- A **task queue** moves slow work (LLM agent runs, document indexing, sending emails, generating reports) **out of the web request** into **background workers**. The API answers immediately with a job ID; a worker picks up the job and does it; the client checks the status later or gets notified.

### Mental model

```text
WITHOUT a queue: user waits for everything
  browser --POST /summarize--> API --(60 s LLM + indexing)--> response    (timeouts, blocked server)

WITH a queue: API only enqueues, workers do the heavy lifting
  browser --POST /summarize--> API --push job--> [ Redis queue ] --pop--> worker 1 (LLM call ...)
          <-- 202 {job_id} --                                    --pop--> worker 2
  browser --GET /jobs/{id}--> API --read status/result from Redis / DB--> {"status": "done", ...}

CACHE: check before doing expensive work
  request -> key = hash(prompt) -> Redis has it?  yes -> return cached answer (1 ms, $0)
                                                  no  -> call LLM -> store with TTL -> return
```

### Why use them?

- **Speed and cost**: cache repeated LLM / embedding / API results.
- **Responsiveness**: long jobs do not block web requests or hit HTTP timeouts.
- **Reliability**: retries for failed jobs; work survives API restarts.
- **Scale**: add more workers to process more jobs in parallel.
- **Rate limiting**: shared counters across all API instances.

### Key terms

| Term | Meaning |
|---|---|
| Key / value | Name and stored data (`user:42:name` -> `"Ana"`) |
| TTL / expiry | Seconds until Redis deletes a key automatically |
| Cache hit / miss | Found in cache / not found (compute and store) |
| Broker | The queue storage that holds jobs (Redis, RabbitMQ) |
| Producer | Code that enqueues jobs (your API) |
| Worker / consumer | Process that runs jobs |
| Job / task | One unit of background work |
| Result backend | Where job results / status are stored |
| Idempotent | Running a job twice has the same effect as once (safe retries) |
| Pub/Sub | Publish messages to channels; subscribers receive them live |

**Where it fits:** used by [39 - FastAPI](39_fastapi.md) apps and [31 - AI Agents](31_ai-agents.md) deployments; runs in [42 - Docker](42_docker.md) / [45 - Kubernetes](45_kubernetes.md); protects against abuse in [37 - AI Security](37_ai-security.md); managed version on [47 - Azure](47_azure.md) (Azure Cache for Redis / Azure Managed Redis).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Redis documentation | https://redis.io/docs/latest/ |
| redis-py | https://redis.readthedocs.io/ |
| Celery | https://docs.celeryq.dev/ |
| RQ | https://python-rq.org/ |
| arq | https://arq-docs.helpmanual.io/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Run Redis](#1-run-redis)
2. [redis-cli Basics](#2-redis-cli-basics)
3. [Data Types](#3-data-types)
4. [Redis from Python](#4-redis-from-python)
5. [Caching Pattern (Cache-Aside)](#5-caching-pattern-cache-aside)
6. [Caching LLM Responses](#6-caching-llm-responses)
7. [Rate Limiting](#7-rate-limiting)
8. [Sessions and Chat History](#8-sessions-and-chat-history)
9. [Pub/Sub and Streams](#9-pubsub-and-streams)
10. [Why Task Queues](#10-why-task-queues)
11. [FastAPI BackgroundTasks (Simplest)](#11-fastapi-backgroundtasks-simplest)
12. [RQ (Redis Queue)](#12-rq-redis-queue)
13. [Celery](#13-celery)
14. [arq (Async Queue)](#14-arq-async-queue)
15. [Job Status and Progress Pattern](#15-job-status-and-progress-pattern)
16. [Retries, Idempotency and Timeouts](#16-retries-idempotency-and-timeouts)
17. [Production Notes](#17-production-notes)
18. [Troubleshooting](#18-troubleshooting)
19. [Try It](#19-try-it)

---

## 0. Flags and Parameters

> Common options for redis-cli and worker commands. Command-line flags connect to the right server and control workers.
>
> Use this when you see `celery -A app.worker worker --loglevel=info --concurrency=4` and want to know what each part does.

```text
celery  -A app.worker  worker  --loglevel=info  --concurrency=4
|       |              |       |                |
|       |              |       |                +-- run 4 tasks in parallel
|       |              |       +------------------- log detail
|       |              +--------------------------- start a worker process
|       +------------------------------------------ -A: module that defines the Celery app
+-------------------------------------------------- task queue CLI
```

| Command | Flag | Meaning |
|---|---|---|
| `redis-cli` | `-h host -p 6379` | Server host / port |
| `redis-cli` | `-a password` / `--user` | Authentication |
| `redis-cli` | `-n 1` | Database number (0 to 15) |
| `redis-cli` | `--tls` | Encrypted connection (cloud Redis) |
| `celery worker` | `--concurrency=4` | Parallel task slots |
| `celery worker` | `-Q emails,llm` | Only consume these queues |
| `celery worker` | `--pool=solo` | Single-thread pool (needed on Windows for development) |
| `celery beat` | | Scheduler for periodic tasks |
| `rq worker` | `high default low` | Queues to listen to, in priority order |
| `rq worker` | `--url redis://...` | Redis connection |
| `arq` | `app.worker.WorkerSettings` | Worker settings class |

---

## 1. Run Redis

> Starting a Redis server. Docker is easiest on every OS (Redis has no official native Windows build).
>
> Use it for local development; production usually uses a managed Redis.

```bash
docker run -d --name redis -p 6379:6379 redis:7
docker exec -it redis redis-cli ping          # PONG

# with persistence and a password
docker run -d --name redis -p 6379:6379 -v redis_data:/data redis:7 \
  redis-server --appendonly yes --requirepass "change-me"
```

Linux: `sudo apt install redis-server`. WSL works too. Other compatible servers: Valkey, KeyDB.

## 2. redis-cli Basics

> The interactive command-line client. Type commands; keys are strings; values have types.
>
> Use it for inspecting caches, debugging queues.

```text
SET greeting "hello"              -> OK
GET greeting                      -> "hello"
SET session:42 "data" EX 3600     -> expires in 1 hour
TTL session:42                    -> seconds left (-1 = no expiry, -2 = gone)
EXPIRE greeting 60
DEL greeting
EXISTS greeting
INCR page_views                   -> atomic counter
KEYS user:*                       -> pattern search (avoid on big production DBs)
SCAN 0 MATCH user:* COUNT 100     -> safe iteration
TYPE mykey
FLUSHDB                           -> delete everything in this DB (careful!)
INFO memory
MONITOR                           -> live view of all commands (debug only)
```

## 3. Data Types

> The value types Redis supports. Each type has its own commands.
>
> Use it for choosing the right structure for your data.

| Type | Use for | Commands |
|---|---|---|
| String | Cached values, JSON blobs, counters | `SET`, `GET`, `INCR`, `EX` |
| Hash | Objects with fields (user profile) | `HSET`, `HGET`, `HGETALL` |
| List | Queues, recent items | `LPUSH`, `RPOP`, `LRANGE`, `BRPOP` |
| Set | Unique items (tags, seen IDs) | `SADD`, `SISMEMBER`, `SMEMBERS` |
| Sorted set | Leaderboards, time-ordered items, rate windows | `ZADD`, `ZRANGE`, `ZREMRANGEBYSCORE` |
| Stream | Durable event logs with consumer groups | `XADD`, `XREADGROUP`, `XACK` |
| JSON / vector (Redis Stack / modules) | Documents, vector search | `JSON.SET`, `FT.SEARCH` |

## 4. Redis from Python

> The `redis` Python client. Create one client (connection pool) and reuse it; `decode_responses=True` returns `str` instead of `bytes`.
>
> Use it in any Python app using Redis.

```powershell
pip install redis
```

```python
import json

import redis

r = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)

r.set("greeting", "hello", ex=60)                 # expires in 60 s
r.get("greeting")
r.incr("counter")
r.hset("user:42", mapping={"name": "Ana", "plan": "pro"})
r.hgetall("user:42")
r.set("config", json.dumps({"model": "claude-opus-5"}))
json.loads(r.get("config"))

pipe = r.pipeline()                               # batch several commands in one round trip
pipe.incr("a").incr("b").expire("a", 60)
pipe.execute()
```

Async version: `import redis.asyncio as aioredis; r = aioredis.from_url(...); await r.get(...)`.

## 5. Caching Pattern (Cache-Aside)

> Check the cache first; compute and store on a miss. A deterministic key from the inputs, a TTL so data does not go stale forever.
>
> Use this when expensive, repeatable results: API calls, DB queries, embeddings, LLM answers.

```python
import functools
import hashlib
import json

CACHE_TTL_SECONDS = 3600


def cached(prefix: str, ttl: int = CACHE_TTL_SECONDS):
    """Cache a function's JSON-serialisable result in Redis, keyed by its arguments."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            raw = json.dumps([args, kwargs], sort_keys=True, default=str)   # stable key
            key = f"{prefix}:{hashlib.sha256(raw.encode()).hexdigest()}"
            if (hit := r.get(key)) is not None:
                return json.loads(hit)
            result = func(*args, **kwargs)
            r.set(key, json.dumps(result), ex=ttl)
            return result
        return wrapper
    return decorator


@cached("weather", ttl=600)
def get_weather(city: str) -> dict:
    return call_weather_api(city)
```

## 6. Caching LLM Responses

> Reusing answers to identical requests. Key = hash of model + system prompt + messages + relevant parameters; only for deterministic-enough use cases.
>
> Use it for repeated FAQ questions, classification of identical texts, embeddings of unchanged documents, eval runs.

```python
def cached_llm(model: str, system: str, user: str, ttl: int = 86_400) -> str:
    key = "llm:" + hashlib.sha256(json.dumps([model, system, user]).encode()).hexdigest()
    if (hit := r.get(key)) is not None:
        return hit
    resp = client.messages.create(model=model, max_tokens=16000, system=system,
                                  messages=[{"role": "user", "content": user}])
    text = "".join(b.text for b in resp.content if b.type == "text")
    r.set(key, text, ex=ttl)
    return text
```

- Exact-match caching only helps when inputs repeat exactly; **semantic caching** (embedding similarity) catches paraphrases but can return wrong answers; use carefully.
- Do not cache personalised or permission-dependent answers across users (include user / tenant in the key).
- Provider **prompt caching** ([26](26_llm-apis.md)) is different: it reduces the cost of a repeated **prefix**, while the answer is still generated.

## 7. Rate Limiting

> Limiting how many requests a user / IP / API key can make. Counters in Redis shared by all API instances; fixed window (simple) or sliding window (smoother).
>
> Use it for public endpoints, expensive LLM routes, protecting provider rate limits and budgets.

```python
import time

from fastapi import HTTPException

LIMIT_PER_MINUTE = 20


def check_rate_limit(user_id: str) -> None:
    """Fixed-window limiter: at most LIMIT_PER_MINUTE requests per user per minute."""
    key = f"rate:{user_id}:{int(time.time() // 60)}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)                 # window cleans itself up
    if count > LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too many requests, try again in a minute.")
```

Libraries: `slowapi` (FastAPI / Starlette), `fastapi-limiter`. Token-based limits (tokens per day per user) work the same with `INCRBY`.

## 8. Sessions and Chat History

> Storing conversation state outside the web process. A list or JSON per session ID with a TTL; any API instance can read it.
>
> Use it for chat apps with several API replicas, stateless containers.

```python
HISTORY_TTL = 60 * 60 * 24
MAX_MESSAGES = 50


def append_message(session_id: str, role: str, content: str) -> None:
    key = f"chat:{session_id}"
    r.rpush(key, json.dumps({"role": role, "content": content}))
    r.ltrim(key, -MAX_MESSAGES, -1)          # keep only the last N messages
    r.expire(key, HISTORY_TTL)


def get_history(session_id: str) -> list[dict]:
    return [json.loads(m) for m in r.lrange(f"chat:{session_id}", 0, -1)]
```

For permanent history, store it in a database (Postgres) and use Redis as a fast cache.

## 9. Pub/Sub and Streams

> Sending messages between processes in real time. Pub/Sub broadcasts to current subscribers (fire and forget); Streams keep messages durably with consumer groups and acknowledgements.
>
> Use it for pushing job progress to the API / browser, event-driven pipelines.

```python
r.publish("job:123:progress", json.dumps({"step": "indexing", "pct": 40}))

sub = r.pubsub()
sub.subscribe("job:123:progress")
for msg in sub.listen():
    if msg["type"] == "message":
        print(json.loads(msg["data"]))

r.xadd("events", {"type": "doc_uploaded", "doc_id": "42"})          # durable stream
```

## 10. Why Task Queues

> When to move work into background jobs. Anything slow, unreliable or scheduled goes to workers; the API stays fast. See the table.

| Task | Why background |
|---|---|
| Agent runs, long LLM chains | Can take minutes; HTTP timeouts |
| Document ingestion / embedding for RAG | CPU / API heavy, many files |
| Batch classification / evals | Thousands of calls |
| Emails, webhooks, notifications | External services can be slow / fail |
| Report generation | Heavy pandas / PDF work |
| Scheduled jobs (nightly re-index) | Run on a timer, not on a request |

## 11. FastAPI BackgroundTasks (Simplest)

> Running a function after the response is sent, in the same process. Add a `BackgroundTasks` parameter and `add_task`.
>
> Use it for small, quick follow-ups (logging, a single email). Not for long / critical jobs: they are lost if the process restarts.

```python
from fastapi import BackgroundTasks


@app.post("/feedback")
def feedback(data: Feedback, tasks: BackgroundTasks):
    tasks.add_task(store_feedback, data)
    return {"status": "received"}
```

## 12. RQ (Redis Queue)

> A simple Python job queue backed by Redis. Enqueue a function call; `rq worker` processes jobs; job status and results are stored in Redis.
>
> Use it for straightforward background jobs with minimal setup (Linux / macOS / WSL / Docker workers).

```powershell
pip install rq
```

```python
# tasks.py
def summarize_document(doc_id: str) -> str:
    text = load_document(doc_id)
    return summarize(text)            # slow LLM call
```

```python
# api.py
from redis import Redis
from rq import Queue

from tasks import summarize_document

q = Queue("default", connection=Redis.from_url("redis://localhost:6379"))
job = q.enqueue(summarize_document, "doc-42", job_timeout=600, retry=None)
job.id

job = q.fetch_job(job.id)
job.get_status()        # queued, started, finished, failed
job.result              # return value when finished
```

```bash
rq worker default --url redis://localhost:6379
```

## 13. Celery

> The most widely used, feature-rich Python task queue. Define a Celery app with a broker (Redis / RabbitMQ); decorate tasks; call `.delay()`; run workers and optionally `beat` for schedules.
>
> Use it for larger systems: retries, rate limits per task, routing to queues, periodic tasks, chains / groups.

```powershell
pip install "celery[redis]"
```

```python
# app/worker.py
from celery import Celery

celery_app = Celery("app", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")
celery_app.conf.task_acks_late = True                 # re-run if a worker dies mid-task
celery_app.conf.beat_schedule = {
    "nightly-reindex": {"task": "app.worker.reindex_all", "schedule": 60 * 60 * 24},
}


@celery_app.task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True, max_retries=5)
def summarize_document(self, doc_id: str) -> str:
    return summarize(load_document(doc_id))


@celery_app.task
def reindex_all() -> int:
    return rebuild_index()
```

```python
result = summarize_document.delay("doc-42")      # enqueue from the API
result.id ; result.status ; result.get(timeout=5)
```

```bash
celery -A app.worker worker --loglevel=info --concurrency=4
celery -A app.worker worker --pool=solo --loglevel=info      # Windows development
celery -A app.worker beat --loglevel=info                     # scheduler
pip install flower && celery -A app.worker flower             # web dashboard on :5555
```

## 14. arq (Async Queue)

> A lightweight asyncio-based job queue on Redis. Jobs are `async def` functions; a worker settings class lists them.
>
> Use it for async codebases (FastAPI + async LLM clients) with many concurrent I/O-bound jobs.

```python
# app/worker.py
from arq.connections import RedisSettings


async def run_agent(ctx, task_id: str, goal: str) -> str:
    return await agent_loop(goal)          # async LLM / tool calls


class WorkerSettings:
    functions = [run_agent]
    redis_settings = RedisSettings(host="localhost")
    max_jobs = 20
    job_timeout = 900
```

```python
from arq import create_pool

redis = await create_pool(RedisSettings())
job = await redis.enqueue_job("run_agent", "t1", "Research topic X")
```

```bash
arq app.worker.WorkerSettings
```

## 15. Job Status and Progress Pattern

> The standard API shape for long-running work. POST creates a job and returns 202 + job ID; GET returns status / progress / result; optionally stream progress events.
>
> Use it for agents, document processing, reports.

```python
@app.post("/jobs", status_code=202)
def create_job(req: JobRequest):
    job = q.enqueue(process, req.model_dump(), job_timeout=900)
    return {"job_id": job.id, "status_url": f"/jobs/{job.id}"}


@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = q.fetch_job(job_id)
    if job is None:
        raise HTTPException(404, "Job not found")
    return {"status": job.get_status(), "progress": job.meta.get("progress"),
            "result": job.result if job.is_finished else None}
```

Workers update progress with `job.meta["progress"] = 40; job.save_meta()` (RQ) or publish events (section 9). Frontends poll every few seconds or listen via SSE / WebSocket.

## 16. Retries, Idempotency and Timeouts

> Making background work reliable. Retry transient failures with backoff; design jobs so re-running is safe; set timeouts.
>
> Use it in every production job.

- **Idempotent jobs**: use upserts, check "already done" flags, deterministic output paths; a retried job must not double-charge or double-send.
- **Retries**: only for transient errors (network, 429, 5xx); not for bugs or invalid input.
- **Timeouts**: per job (`job_timeout`, Celery `time_limit`) so stuck jobs are killed.
- **Dead-letter**: keep failed jobs for inspection (RQ failed registry, Celery results) and alert.
- **Small payloads**: pass IDs, not huge documents; workers load data from storage.

## 17. Production Notes

> Running Redis and workers safely at scale. Managed Redis, authentication, persistence choices, monitoring.
>
> Use it for going live.

- Use a managed Redis (Azure Managed Redis / Cache for Redis, AWS ElastiCache, Redis Cloud) with TLS and auth.
- Never expose Redis to the internet without auth / network rules.
- Decide persistence: pure cache (no persistence needed) vs queues / sessions (enable AOF / snapshots or use a durable broker).
- Set `maxmemory` and an eviction policy (`allkeys-lru` for pure caches).
- Monitor queue length, job failures, worker count, memory; scale workers on queue depth (KEDA on Kubernetes, [45](45_kubernetes.md)).
- Run workers as separate containers / services from the API ([42](42_docker.md)).

## 18. Troubleshooting

| Problem | Fix |
|---|---|
| `ConnectionError: Error 10061 connecting to localhost:6379` | Redis not running; `docker ps`; check host / port |
| `NOAUTH Authentication required` | Add password to URL: `redis://:password@host:6379/0` |
| Values come back as `b'...'` bytes | `decode_responses=True` |
| Cache never hits | Key not deterministic (unsorted JSON, timestamps in key) |
| Stale data served | TTL too long; delete keys when data changes |
| Jobs stay "queued" forever | No worker running / listening to that queue name |
| Celery on Windows hangs / errors | Use `--pool=solo` for development, or run workers in WSL / Docker |
| Job lost when worker crashed | Celery `task_acks_late=True`; idempotent jobs; durable broker settings |
| Memory keeps growing | Keys without TTL; set expiry, `maxmemory` + eviction policy |
| `Can't pickle` / serialisation errors | Pass simple JSON-able arguments (IDs, strings), not clients or open files |

## 19. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Keys with expiry

Start Redis in Docker, store a key that expires after 60 seconds and check the remaining time.

<details markdown="1">
<summary>Solution</summary>

```bash
docker run -d --name redis -p 6379:6379 redis:7
docker exec -it redis redis-cli SET greeting hello EX 60
docker exec -it redis redis-cli TTL greeting
```

</details>

### Exercise 2: Rate limit

Allow at most 10 requests per user per minute.

<details markdown="1">
<summary>Solution</summary>

```python
key = f"rate:{user_id}:{int(time.time() // 60)}"
count = r.incr(key)
if count == 1:
    r.expire(key, 60)
if count > 10:
    raise HTTPException(429, "Too many requests")
```

</details>

### Exercise 3: Background job

Enqueue `summarize_document("doc-42")` with RQ and check its status.

<details markdown="1">
<summary>Solution</summary>

```python
job = Queue(connection=Redis()).enqueue(summarize_document, "doc-42", job_timeout=600)
job.get_status()          # queued -> started -> finished
```

Start a worker with `rq worker`.

</details>

---

<!-- nav:start -->
**Previous:** [40 - Uvicorn (ASGI Server)](40_uvicorn.md) | **Index:** [All guides](README.md) | **Next:** [42 - Docker](42_docker.md)
<!-- nav:end -->
