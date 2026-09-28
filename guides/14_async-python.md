# 14 - Async Python

<!-- nav:start -->
**Previous:** [13 - Pydantic](13_pydantic.md) | **Index:** [All guides](../README.md) | **Next:** [15 - pytest](15_pytest.md)
<!-- nav:end -->

Quick reference for asynchronous programming in Python with `async` / `await` and `asyncio`: running many slow I/O tasks (API calls, LLM requests, database queries) at the same time.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### Before you start

**You should know:** Python functions and exceptions ([10 - Python Basics](10_python-basics.md)), and that an API call is a request over the network that takes time to answer ([09 - HTTP and APIs](09_http-apis.md)). Async is an intermediate topic: it is fine to skip it until you need to make many slow calls at once.

**The problem it solves:** you need 100 answers from an LLM, and each takes 5 seconds. Called one after another, that is over 8 minutes, and your program sits idle almost the whole time, just waiting for the network. A web server handling many users has the same problem: one slow request should not block everyone else.

**Before async:** the usual answer was threads (several lines of work running "at once"), which work but are harder to reason about and heavier when you need thousands. Python added `async` / `await` (Python 3.5, 2015) as a lighter way for one program to juggle many waiting operations. FastAPI and the LLM SDKs support it directly.

**Think of it like:** the chef in the mental model below, who puts the pasta on to boil and starts the bread while waiting, instead of staring at the pot.

### What is async programming?

Most time in web and AI apps is spent **waiting**: for an LLM to answer, a database to return rows, a file to download. Normal (synchronous) Python waits idle for each call to finish before starting the next. **Async** Python lets one program start many operations and switch to other work while each one waits. It is not about using more CPU cores; it is about **not wasting time waiting**.

### Mental model

Imagine a chef cooking 3 dishes:

```text
Synchronous chef (one thing at a time):
  boil pasta [==========wait==========] -> bake bread [=====wait=====] -> make soup [====wait====]
  total time = sum of all waits

Async chef (switches while waiting):
  start pasta ---wait--------------------------> done
  start bread    ---wait-------------> done
  start soup        ---wait--------> done
  total time = roughly the longest single wait
```

The **event loop** is the chef: a single loop that runs tasks until each hits an `await` (a waiting point), then switches to another task that is ready. `async def` defines a task that *can* pause; `await` marks *where* it pauses.

| Kind of work | Async helps? | Use instead |
|---|---|---|
| I/O-bound (HTTP, LLM APIs, DB, files, network) | Yes, a lot | `asyncio` |
| CPU-bound (maths, pandas, model inference) | No (blocks the loop) | `multiprocessing`, `ProcessPoolExecutor` |
| Blocking library with no async version | Only via threads | `asyncio.to_thread(...)` |

### Why learn it?

- **Parallel LLM calls**: summarise 100 documents in the time of ~10 instead of 100 sequential calls.
- **FastAPI** is async; knowing when to use `async def` vs `def` avoids freezing your server.
- **Agents and streaming** (tokens arriving over time) are naturally async.
- **Most AI SDKs** have async clients (`AsyncAnthropic`, `AsyncOpenAI`, `httpx.AsyncClient`).

### Key terms

| Term | Meaning |
|---|---|
| Coroutine | What calling an `async def` function returns; it does nothing until awaited |
| `await` | Pause here until the awaited thing finishes; let other tasks run |
| Event loop | The scheduler that runs coroutines and switches between them |
| Task | A coroutine scheduled to run concurrently (`asyncio.create_task`) |
| Concurrency | Many tasks in progress at once (interleaved) |
| Parallelism | Many tasks running at the exact same time on several cores |
| Blocking call | A normal function that waits without letting others run (`time.sleep`, `requests.get`) |
| Semaphore | A limit on how many tasks may run a section at once |

**Where it fits:** used with [09 - HTTP and APIs](09_http-apis.md) (httpx), [27 - LLM APIs](27_llm-apis.md) (async clients), [40 - FastAPI](40_fastapi.md), [32 - AI Agents](32_ai-agents.md); tested with [15 - pytest](15_pytest.md) (pytest-asyncio).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| asyncio documentation | https://docs.python.org/3/library/asyncio.html |
| HTTPX async support | https://www.python-httpx.org/async/ |

---

## Contents

1. [async def and await](#1-async-def-and-await)
2. [Running Async Code](#2-running-async-code)
3. [Running Tasks Concurrently (gather)](#3-running-tasks-concurrently-gather)
4. [Tasks and TaskGroup](#4-tasks-and-taskgroup)
5. [Limiting Concurrency (Semaphore)](#5-limiting-concurrency-semaphore)
6. [Timeouts](#6-timeouts)
7. [Error Handling](#7-error-handling)
8. [Processing Results as They Finish](#8-processing-results-as-they-finish)
9. [Async HTTP with httpx](#9-async-http-with-httpx)
10. [Async LLM Calls](#10-async-llm-calls)
11. [Async Iterators and Streaming](#11-async-iterators-and-streaming)
12. [Async Context Managers](#12-async-context-managers)
13. [Calling Blocking Code from Async](#13-calling-blocking-code-from-async)
14. [Queues: Producer / Consumer](#14-queues-producer--consumer)
15. [Async in Jupyter and FastAPI](#15-async-in-jupyter-and-fastapi)
16. [Threads vs Processes vs Async](#16-threads-vs-processes-vs-async)
17. [Troubleshooting](#17-troubleshooting)
18. [Try It](#18-try-it)

---

## 1. async def and await

> The two keywords that define and use asynchronous functions. `async def` creates a coroutine function; inside it, `await` another coroutine to wait for its result without blocking others.
>
> Use it in any function that does I/O through an async library.

```python
import asyncio


async def fetch_price(item: str) -> float:
    """Pretend to call an API that takes 1 second."""
    await asyncio.sleep(1)          # non-blocking wait (NOT time.sleep)
    return 9.99


async def main():
    price = await fetch_price("lamp")     # waits 1 s, but other tasks could run meanwhile
    print(price)
```

- You can only use `await` inside `async def`.
- Calling `fetch_price("lamp")` without `await` returns a coroutine object and does nothing.

## 2. Running Async Code

> Starting the event loop from normal code. `asyncio.run(main())` creates a loop, runs `main` to completion, and closes the loop.
>
> Use it for the single entry point of an async script.

```python
if __name__ == "__main__":
    asyncio.run(main())
```

Call `asyncio.run` once at the top level, not inside other async functions.

## 3. Running Tasks Concurrently (gather)

> Starting several coroutines at once and waiting for all of them. `asyncio.gather(*coroutines)` runs them concurrently and returns results in the same order.
>
> Use this when many independent API / LLM calls.

```python
import time


async def main():
    start = time.perf_counter()
    prices = await asyncio.gather(
        fetch_price("lamp"),
        fetch_price("chair"),
        fetch_price("desk"),
    )
    print(prices, f"{time.perf_counter() - start:.1f}s")     # [9.99, 9.99, 9.99] 1.0s (not 3.0s)

    items = ["a", "b", "c", "d"]
    results = await asyncio.gather(*(fetch_price(i) for i in items))   # from a list
```

## 4. Tasks and TaskGroup

> Scheduling coroutines to run in the background while you do other things. `asyncio.create_task` starts a coroutine now; `TaskGroup` (Python 3.11+) starts several and waits for all, cancelling the rest if one fails.
>
> Use it for background work, or structured concurrency with safe error handling.

```python
async def main():
    task = asyncio.create_task(fetch_price("lamp"))     # starts running right away
    await do_other_things()
    price = await task                                  # collect the result later

    async with asyncio.TaskGroup() as tg:               # all tasks finish before the block exits
        t1 = tg.create_task(fetch_price("a"))
        t2 = tg.create_task(fetch_price("b"))
    print(t1.result(), t2.result())
```

Keep a reference to tasks you create; unreferenced tasks can be garbage-collected.

## 5. Limiting Concurrency (Semaphore)

> Allowing at most N tasks to run a section at the same time. `async with semaphore:` waits for a free slot before entering.
>
> Use it for respecting API rate limits when launching hundreds of calls.

```python
MAX_CONCURRENT = 5


async def summarize_all(docs: list[str]) -> list[str]:
    """Summarize many documents, at most 5 LLM calls at a time."""
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async def one(doc: str) -> str:
        async with sem:                       # only 5 inside this block at once
            return await summarize(doc)

    return await asyncio.gather(*(one(d) for d in docs))
```

## 6. Timeouts

> Giving up on something that takes too long. `asyncio.timeout(seconds)` (3.11+) or `asyncio.wait_for(coro, timeout)` raises `TimeoutError`.
>
> Use it in any external call that might hang.

```python
async def main():
    try:
        async with asyncio.timeout(5):
            result = await slow_call()
    except TimeoutError:
        result = None

    result = await asyncio.wait_for(slow_call(), timeout=5)     # older style
```

## 7. Error Handling

> What happens when one of many concurrent tasks fails. `gather` raises the first error by default; `return_exceptions=True` returns errors as values instead; `TaskGroup` raises an `ExceptionGroup`.
>
> Use it for batch jobs where one failure should not lose all other results.

```python
results = await asyncio.gather(*coros, return_exceptions=True)
for item, res in zip(items, results):
    if isinstance(res, Exception):
        logger.warning("failed %s: %s", item, res)
    else:
        save(res)

try:
    async with asyncio.TaskGroup() as tg:
        ...
except* ValueError as eg:                 # handle a group of ValueErrors (3.11+)
    for e in eg.exceptions:
        logger.error(e)
```

## 8. Processing Results as They Finish

> Handling each result as soon as it is ready, instead of waiting for the slowest. `asyncio.as_completed` yields awaitables in completion order.
>
> Use it for progress bars, streaming results to a UI, saving results early.

```python
for next_done in asyncio.as_completed([fetch_price(i) for i in items]):
    price = await next_done
    print("got", price)
```

## 9. Async HTTP with httpx

> Making many HTTP requests concurrently. One shared `httpx.AsyncClient` (reuses connections) + `gather`.
>
> Use it for scraping, calling several APIs, webhooks. Sync `requests` would block the loop.

```python
import httpx


async def fetch_all(urls: list[str]) -> list[int]:
    async with httpx.AsyncClient(timeout=10) as client:
        responses = await asyncio.gather(*(client.get(u) for u in urls), return_exceptions=True)
    return [r.status_code if isinstance(r, httpx.Response) else -1 for r in responses]
```

## 10. Async LLM Calls

> Calling an LLM for many inputs concurrently. Use the SDK's async client with `await`, plus a semaphore for rate limits.
>
> Use it for classifying / summarising / extracting over many documents.

```python
import anthropic

client = anthropic.AsyncAnthropic()
sem = asyncio.Semaphore(8)


async def classify(text: str) -> str:
    async with sem:
        msg = await client.messages.create(
            model="claude-opus-5",
            max_tokens=256,
            messages=[{"role": "user", "content": f"Label as positive/negative/neutral. Reply with the label only.\n\n{text}"}],
        )
    return next(b.text for b in msg.content if b.type == "text").strip()


async def main(texts: list[str]):
    labels = await asyncio.gather(*(classify(t) for t in texts))
```

For very large offline jobs, the provider's **batch API** is cheaper than many parallel calls (see [27 - LLM APIs](27_llm-apis.md)).

## 11. Async Iterators and Streaming

> Looping over values that arrive over time. `async for` over an async iterator; write your own with `async def` + `yield` (async generator).
>
> Use it for LLM token streams, reading a stream of events, paginated APIs.

```python
async def stream_answer(question: str):
    async with client.messages.stream(
        model="claude-opus-5",
        max_tokens=16000,
        messages=[{"role": "user", "content": question}],
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)


async def numbers(n: int):                  # async generator
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async for x in numbers(3):
    print(x)
```

## 12. Async Context Managers

> Setup / cleanup that itself needs `await` (open connections, sessions). `async with` calls `__aenter__` / `__aexit__`; build your own with `@asynccontextmanager`.
>
> Use it for HTTP clients, DB connections, FastAPI lifespan.

```python
from contextlib import asynccontextmanager


@asynccontextmanager
async def db_connection():
    conn = await connect()
    try:
        yield conn
    finally:
        await conn.close()


async with db_connection() as conn:
    rows = await conn.fetch("SELECT 1")
```

## 13. Calling Blocking Code from Async

> Using normal (sync) functions without freezing the event loop. `asyncio.to_thread(func, *args)` runs it in a thread; CPU-heavy work goes to a process pool.
>
> Use this when a library has no async version (pandas, some SDKs, file parsing).

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

df = await asyncio.to_thread(pd.read_csv, "big.csv")        # I/O-ish blocking call

loop = asyncio.get_running_loop()
with ProcessPoolExecutor() as pool:
    result = await loop.run_in_executor(pool, heavy_cpu_function, data)
```

## 14. Queues: Producer / Consumer

> Tasks passing work to each other through a queue. Producers `put` items; a fixed number of workers `get` and process them.
>
> Use it for pipelines (download -> parse -> embed), controlled worker pools.

```python
async def worker(name: str, queue: asyncio.Queue):
    while True:
        item = await queue.get()
        try:
            await process(item)
        finally:
            queue.task_done()


async def main(items):
    queue: asyncio.Queue = asyncio.Queue()
    for item in items:
        queue.put_nowait(item)
    workers = [asyncio.create_task(worker(f"w{i}", queue)) for i in range(4)]
    await queue.join()                       # wait until every item is processed
    for w in workers:
        w.cancel()
```

## 15. Async in Jupyter and FastAPI

> Environments that already run an event loop. Jupyter and FastAPI own the loop; you just `await` directly.
>
> Use it for notebooks and web endpoints.

```python
# Jupyter: top-level await works directly (no asyncio.run)
results = await asyncio.gather(*(classify(t) for t in texts))
```

```python
# FastAPI: async endpoint with async libraries
@app.get("/prices")
async def prices():
    return await asyncio.gather(fetch_price("a"), fetch_price("b"))
```

In FastAPI use plain `def` for blocking code (FastAPI runs it in a thread for you). See [40 - FastAPI](40_fastapi.md).

## 16. Threads vs Processes vs Async

> The three ways to do several things at once in Python. They differ in what they share and what they speed up.
>
> Use it for pick by the type of work.

| | Async (`asyncio`) | Threads (`threading`, `ThreadPoolExecutor`) | Processes (`multiprocessing`, `ProcessPoolExecutor`) |
|---|---|---|---|
| Good for | Lots of I/O with async libraries | I/O with blocking libraries | CPU-heavy work |
| Parallel CPU | No | No (GIL, except free-threaded builds) | Yes |
| Scale | 1000s of tasks | 10s to 100s | Number of cores |
| Overhead | Very low | Low | High (separate memory) |
| Example | 500 LLM calls | 20 downloads with `requests` | Parallel feature engineering |

## 17. Troubleshooting

| Problem | Fix |
|---|---|
| `RuntimeWarning: coroutine '...' was never awaited` | Add `await` before the call |
| `SyntaxError: 'await' outside async function` | Put the code in an `async def` |
| `RuntimeError: asyncio.run() cannot be called from a running event loop` | In Jupyter / FastAPI just `await`; do not call `asyncio.run` |
| Async code is not faster | Using blocking calls (`requests`, `time.sleep`); switch to `httpx`, `asyncio.sleep`, async SDK clients |
| Whole app freezes | CPU-heavy or blocking code inside `async def`; use `to_thread` / process pool |
| 429 rate limit errors | Add a `Semaphore`, reduce concurrency, respect `retry-after` |
| One failure cancels everything | `gather(..., return_exceptions=True)` |
| `Task was destroyed but it is pending` | Program exited before tasks finished; await or cancel them properly |
| `Event loop is closed` (Windows) | Close clients inside the loop (`async with`), avoid reusing clients across `asyncio.run` calls |

## 18. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Concurrency proof

Run three tasks that each sleep 1 second so the total takes about 1 second.

<details markdown="1">
<summary>Solution</summary>

```python
import asyncio
import time


async def work(i: int) -> int:
    await asyncio.sleep(1)
    return i


async def main():
    start = time.perf_counter()
    print(await asyncio.gather(work(1), work(2), work(3)), round(time.perf_counter() - start, 1))

asyncio.run(main())      # [1, 2, 3] 1.0
```

</details>

### Exercise 2: At most 5 at once

Call an async function for 100 items with at most 5 running at the same time.

<details markdown="1">
<summary>Solution</summary>

```python
sem = asyncio.Semaphore(5)


async def limited(item):
    async with sem:
        return await call(item)

results = await asyncio.gather(*(limited(i) for i in items))
```

</details>

### Exercise 3: Timeout

Give `slow_call()` at most 2 seconds and fall back to `None`.

<details markdown="1">
<summary>Solution</summary>

```python
try:
    async with asyncio.timeout(2):
        result = await slow_call()
except TimeoutError:
    result = None
```

</details>

---

<!-- nav:start -->
**Previous:** [13 - Pydantic](13_pydantic.md) | **Index:** [All guides](../README.md) | **Next:** [15 - pytest](15_pytest.md)
<!-- nav:end -->
