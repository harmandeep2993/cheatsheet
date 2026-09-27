# 08 - HTTP and APIs

Quick reference for how the web and APIs work: HTTP requests and responses, REST design, authentication, streaming, and calling APIs from the terminal and Python.

## Introduction

### What is HTTP and what is an API?

**HTTP** (HyperText Transfer Protocol) is the language computers use to talk over the web. A **client** (browser, Python script, mobile app) sends a **request** to a **server**, and the server sends back a **response**. Every web page, every LLM call to Claude or OpenAI, and every FastAPI endpoint uses HTTP.

An **API** (Application Programming Interface) is a set of URLs (**endpoints**) that a program exposes so other programs can use it. A **REST API** uses HTTP methods (GET, POST, ...) on resource URLs (`/users/42`) and usually sends **JSON**.

### Mental model

Think of a restaurant: you (client) give an **order** (request) to the waiter with a specific **dish** (URL), an **action** (method), **special notes** (headers) and maybe **details** (body). The kitchen (server) returns a **plate** (response) with a **status** (success, not available, your fault, our fault).

```text
CLIENT                                                   SERVER
  |  POST /v1/messages HTTP/1.1                             |
  |  Host: api.anthropic.com                                |
  |  x-api-key: sk-ant-...           <- headers (metadata)  |
  |  content-type: application/json                         |
  |                                                         |
  |  {"model": "...", "messages": [...]}  <- body (data)    |
  | ------------------------------------------------------> |
  |                                                         |  runs code
  |  HTTP/1.1 200 OK                  <- status code        |
  |  content-type: application/json                         |
  |                                                         |
  |  {"content": [{"type": "text", "text": "Hi!"}]}         |
  | <------------------------------------------------------ |
```

Every API call you ever make, whatever library you use, is this: **method + URL + headers + body -> status + headers + body**.

### Why learn it?

- **Every AI app is HTTP**: SDKs like `anthropic` and `openai` just build these requests for you.
- **Debugging**: 401 vs 404 vs 429 vs 500 tells you immediately what went wrong.
- **Building APIs** with FastAPI requires knowing methods, status codes and headers.
- **Integration**: webhooks, OAuth logins, third-party services all follow the same rules.

### Key terms

| Term | Meaning |
|---|---|
| Client / server | Who asks / who answers |
| Endpoint | A URL + method that does one thing (`POST /v1/messages`) |
| Method (verb) | What to do: GET, POST, PUT, PATCH, DELETE |
| Header | Key-value metadata (auth, content type) |
| Body / payload | The data sent, usually JSON |
| Status code | 3-digit result: 2xx ok, 4xx client error, 5xx server error |
| Query string | `?key=value` parameters in the URL |
| REST | Style of API built around resources and HTTP methods |
| Idempotent | Repeating the request has the same effect as doing it once (GET, PUT, DELETE) |
| Rate limit | Max requests allowed per time window |
| SSE | Server-Sent Events: server streams chunks over one response (LLM streaming) |
| Webhook | The server calls YOUR URL when something happens |

**Where it fits:** the foundation for [26 - LLM APIs](26_llm-apis.md) and [39 - FastAPI](39_fastapi.md); data formats in [07 - YAML and JSON](07_yaml-json.md); HTTPS and proxies in [43 - Nginx and HTTPS](43_nginx-https.md).

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Anatomy of a URL](#1-anatomy-of-a-url)
2. [HTTP Methods](#2-http-methods)
3. [Status Codes](#3-status-codes)
4. [Headers](#4-headers)
5. [Request and Response Bodies](#5-request-and-response-bodies)
6. [REST API Design](#6-rest-api-design)
7. [Authentication](#7-authentication)
8. [curl](#8-curl)
9. [PowerShell (Invoke-RestMethod)](#9-powershell-invoke-restmethod)
10. [Python requests](#10-python-requests)
11. [Python httpx (Sync and Async)](#11-python-httpx-sync-and-async)
12. [Timeouts and Retries](#12-timeouts-and-retries)
13. [Rate Limits](#13-rate-limits)
14. [Pagination](#14-pagination)
15. [Streaming (SSE)](#15-streaming-sse)
16. [Webhooks](#16-webhooks)
17. [CORS](#17-cors)
18. [HTTPS and TLS](#18-https-and-tls)
19. [REST vs GraphQL vs gRPC vs WebSocket](#19-rest-vs-graphql-vs-grpc-vs-websocket)
20. [Troubleshooting](#20-troubleshooting)

---

## 0. Flags and Parameters

> - **What:** The curl flags used most with APIs.
> - **How:** `curl [flags] URL`; flags set method, headers, body and output.
> - **When to use:** You see `curl -X POST -H "..." -d '{...}' URL` and want to know what each part does.

```text
curl  -X POST  https://api.example.com/items  -H "Content-Type: application/json"  -d '{"name": "Lamp"}'
|     |        |                              |                                    |
|     |        |                              |                                    +-- -d: request body (data)
|     |        |                              +--------------------------------------- -H: add a header
|     |        +---------------------------------------------------------------------- URL (endpoint)
|     +------------------------------------------------------------------------------- -X: HTTP method
+------------------------------------------------------------------------------------- program
```

| Flag | Long form | Meaning |
|---|---|---|
| `-X POST` | `--request` | HTTP method (default GET, or POST when `-d` is used) |
| `-H "K: V"` | `--header` | Add a header (repeat for several) |
| `-d '...'` | `--data` | Request body |
| `--json '...'` | | Body + JSON content-type and accept headers (curl 7.82+) |
| `-i` | `--include` | Show response headers too |
| `-I` | `--head` | Headers only (HEAD request) |
| `-v` | `--verbose` | Show everything sent and received (debugging) |
| `-s` | `--silent` | No progress bar |
| `-o file` | `--output` | Save body to a file |
| `-L` | `--location` | Follow redirects |
| `-u user:pass` | `--user` | Basic authentication |
| `-N` | `--no-buffer` | Print streamed chunks immediately (SSE) |
| `-w "%{http_code}"` | `--write-out` | Print extra info, e.g. status code |
| `--max-time 10` | | Give up after 10 seconds |

---

## 1. Anatomy of a URL

> - **What:** The parts of a web address.
> - **How:** Scheme, host, port, path, query and fragment, each with a job.
> - **When to use:** Building request URLs, reading API docs, debugging wrong endpoints.

```text
https://api.example.com:443/v1/users/42/orders?status=open&limit=10#top
|____|  |_____________||__||__________________||_____________________||__|
scheme  host            port path (resource)   query string           fragment
```

| Part | Meaning |
|---|---|
| Scheme | `http` (plain) or `https` (encrypted) |
| Host | Server name (DNS resolves it to an IP) |
| Port | Door on the server; default 80 (http), 443 (https); dev servers often 8000 |
| Path | Which resource: `/v1/users/42/orders` |
| Query | Options / filters: `?status=open&limit=10` |
| Fragment | Browser-only position, never sent to the server |

Special characters in queries must be URL-encoded (`space` -> `%20`); libraries do this when you pass `params=`.

## 2. HTTP Methods

> - **What:** The verb that says what the request wants to do.
> - **How:** Each method has a meaning servers and caches rely on.
> - **When to use:** Choosing the method when calling or designing an endpoint.

| Method | Meaning | Body? | Safe | Idempotent | Example |
|---|---|---|---|---|---|
| GET | Read | No | Yes | Yes | `GET /users/42` |
| POST | Create / run an action | Yes | No | No | `POST /users`, `POST /v1/messages` |
| PUT | Replace entirely | Yes | No | Yes | `PUT /users/42` |
| PATCH | Update some fields | Yes | No | No* | `PATCH /users/42` |
| DELETE | Remove | Usually no | No | Yes | `DELETE /users/42` |
| HEAD | Like GET, headers only | No | Yes | Yes | Check if a file exists |
| OPTIONS | What is allowed (CORS preflight) | No | Yes | Yes | Sent by browsers |

**Safe** = does not change anything. **Idempotent** = sending it twice has the same result as once (safe to retry).

## 3. Status Codes

> - **What:** The 3-digit number that says how the request went.
> - **How:** The first digit is the category; the rest gives detail.
> - **When to use:** First thing to check when something fails.

| Code | Name | Meaning / typical cause |
|---|---|---|
| **2xx** | **Success** | |
| 200 | OK | Worked, body has the result |
| 201 | Created | New resource created |
| 202 | Accepted | Queued for later processing |
| 204 | No Content | Worked, nothing to return |
| **3xx** | **Redirect** | |
| 301 / 308 | Moved Permanently | Use the new URL (in `Location` header) |
| 302 / 307 | Temporary redirect | Follow with `-L` / `follow_redirects=True` |
| 304 | Not Modified | Cached copy is still valid |
| **4xx** | **Client error (your request is wrong)** | |
| 400 | Bad Request | Malformed JSON, invalid parameter |
| 401 | Unauthorized | Missing / wrong API key or token |
| 403 | Forbidden | Authenticated but not allowed |
| 404 | Not Found | Wrong URL, ID does not exist, wrong model name |
| 405 | Method Not Allowed | GET instead of POST, etc. |
| 409 | Conflict | Duplicate / version conflict |
| 413 | Payload Too Large | Body too big |
| 415 | Unsupported Media Type | Missing `Content-Type: application/json` |
| 422 | Unprocessable Entity | Valid JSON but fails validation (FastAPI) |
| 429 | Too Many Requests | Rate limit; wait (see `retry-after`) and retry |
| **5xx** | **Server error (not your fault)** | |
| 500 | Internal Server Error | Bug / crash on the server |
| 502 | Bad Gateway | Proxy could not reach the app behind it |
| 503 | Service Unavailable | Overloaded or down; retry later |
| 504 | Gateway Timeout | Upstream took too long |
| 529 | Overloaded | Used by some APIs (Anthropic) when busy; retry with backoff |

Rule of thumb: **retry** 408, 429, 5xx (with backoff); **fix your request** for other 4xx.

## 4. Headers

> - **What:** Key-value metadata sent with requests and responses.
> - **How:** Case-insensitive names; the server and client use them for auth, formats, caching and limits.
> - **When to use:** Every authenticated API call; debugging content-type and rate-limit issues.

| Header | Direction | Meaning |
|---|---|---|
| `Content-Type: application/json` | both | Format of the body |
| `Accept: application/json` | request | Format you want back |
| `Authorization: Bearer <token>` | request | Token authentication |
| `x-api-key: <key>` | request | API key (Anthropic and others) |
| `User-Agent` | request | Which client is calling |
| `Cache-Control` | both | Caching rules |
| `retry-after: 30` | response | Seconds to wait before retrying (429 / 503) |
| `x-ratelimit-remaining-*` | response | Requests / tokens left in the window |
| `Location` | response | URL of a new resource or redirect target |
| `Set-Cookie` / `Cookie` | both | Session cookies |
| `request-id` | response | ID to quote when reporting a problem |

## 5. Request and Response Bodies

> - **What:** The actual data carried by a request or response.
> - **How:** Usually JSON; forms and file uploads use other content types.
> - **When to use:** Sending data (POST / PUT / PATCH) and reading results.

| Content-Type | Used for |
|---|---|
| `application/json` | Almost all APIs |
| `application/x-www-form-urlencoded` | Classic HTML forms, OAuth token requests |
| `multipart/form-data` | File uploads |
| `text/event-stream` | Streaming (SSE) responses |
| `application/octet-stream` | Raw binary files |

## 6. REST API Design

> - **What:** Conventions for designing clear, predictable APIs.
> - **How:** Nouns for resources in URLs, HTTP methods for actions, status codes for results, JSON bodies.
> - **When to use:** Designing endpoints in [39 - FastAPI](39_fastapi.md).

| Action | Method + path | Success |
|---|---|---|
| List orders | `GET /orders?status=open&limit=20` | 200 |
| Get one order | `GET /orders/42` | 200 / 404 |
| Create order | `POST /orders` | 201 |
| Replace order | `PUT /orders/42` | 200 |
| Update fields | `PATCH /orders/42` | 200 |
| Delete order | `DELETE /orders/42` | 204 |
| Nested resource | `GET /customers/7/orders` | 200 |
| Action that is not CRUD | `POST /orders/42/cancel` | 200 |

- Use plural nouns (`/orders`), not verbs (`/getOrders`).
- Version your API: `/v1/...`.
- Return consistent error bodies: `{"detail": "Order not found"}`.

## 7. Authentication

> - **What:** Proving who is calling.
> - **How:** A secret or token travels in a header on every request; the server checks it.
> - **When to use:** Every non-public API. Keep secrets in environment variables, never in code or Git.

| Method | How it looks | Used by |
|---|---|---|
| API key | `x-api-key: sk-...` or `Authorization: Bearer sk-...` | LLM APIs, most SaaS APIs |
| Basic auth | `Authorization: Basic base64(user:pass)` | Simple internal tools |
| Bearer token / JWT | `Authorization: Bearer eyJhbGci...` | Logged-in users, OAuth |
| OAuth 2.0 | App gets a token after the user approves ("Log in with Google") | Access to user data in other services |
| Cookie session | `Cookie: session=...` | Browser web apps |
| mTLS | Client certificate | High-security service-to-service |

**JWT** (JSON Web Token): three base64 parts `header.payload.signature`; the server verifies the signature and reads user info from the payload without a database lookup. Anyone can decode the payload, so never put secrets in it.

## 8. curl

> - **What:** The universal command-line HTTP client.
> - **How:** Build requests with flags (see section 0).
> - **When to use:** Quick tests, reproducing bugs, examples in docs.

```bash
curl https://httpbin.org/get                                   # GET
curl "https://httpbin.org/get?city=Berlin&days=3"              # query string (quote it!)
curl -i https://httpbin.org/status/404                          # see status + headers
curl -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" \
  -d '{"name": "Lamp", "price": 25}'                           # JSON body
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/me
curl -F "file=@report.csv" https://api.example.com/upload       # file upload (multipart)
curl -s https://api.github.com/users/octocat | jq .name        # pipe to jq
curl -o model.bin -L https://example.com/download              # download, follow redirects
curl -s -o /dev/null -w "%{http_code}\n" https://example.com   # status code only
```

Windows PowerShell: use `curl.exe` (plain `curl` is an alias for `Invoke-WebRequest` in 5.1) and escape inner quotes: `-d "{\"name\": \"Lamp\"}"`.

## 9. PowerShell (Invoke-RestMethod)

> - **What:** PowerShell's built-in HTTP client that parses JSON automatically.
> - **How:** `Invoke-RestMethod` returns objects; `ConvertTo-Json` builds bodies.
> - **When to use:** Scripting API calls on Windows without escaping headaches.

```powershell
$r = Invoke-RestMethod https://api.github.com/users/octocat
$r.name

$body = @{ name = "Lamp"; price = 25 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri https://httpbin.org/post `
  -ContentType "application/json" -Body $body `
  -Headers @{ Authorization = "Bearer $env:API_TOKEN" }

Invoke-WebRequest https://example.com -OutFile page.html       # raw response / download
```

## 10. Python requests

> - **What:** The classic, simple HTTP library for Python.
> - **How:** One function per method; `json=` sends JSON, `params=` builds the query, `.json()` parses the response.
> - **When to use:** Scripts and synchronous code.

```python
import os

import requests

r = requests.get(
    "https://api.example.com/items",
    params={"limit": 10, "status": "open"},
    headers={"Authorization": f"Bearer {os.environ['API_TOKEN']}"},
    timeout=10,                                  # ALWAYS set a timeout
)
r.status_code          # 200
r.headers["content-type"]
r.raise_for_status()   # raise an exception for 4xx / 5xx
data = r.json()

r = requests.post("https://api.example.com/items", json={"name": "Lamp"}, timeout=10)

with requests.Session() as s:                    # reuse connection + default headers
    s.headers.update({"Authorization": "Bearer ..."})
    s.get("https://api.example.com/me", timeout=10)

with open("report.csv", "rb") as f:
    requests.post(url, files={"file": f}, timeout=30)          # upload
```

## 11. Python httpx (Sync and Async)

> - **What:** A modern HTTP library with the same style as requests plus async support.
> - **How:** `httpx.Client` for sync, `httpx.AsyncClient` with `await` for async.
> - **When to use:** Async apps (FastAPI endpoints), many concurrent calls, HTTP/2.

```python
import asyncio

import httpx

with httpx.Client(timeout=10, base_url="https://api.example.com") as client:
    r = client.get("/items", params={"limit": 5})
    r.raise_for_status()


async def fetch_all(urls: list[str]) -> list[dict]:
    """Fetch many URLs concurrently."""
    async with httpx.AsyncClient(timeout=10) as client:
        responses = await asyncio.gather(*(client.get(u) for u in urls))
    return [r.json() for r in responses]
```

See [13 - Async Python](13_async-python.md).

## 12. Timeouts and Retries

> - **What:** Protecting your app from slow or failing servers.
> - **How:** A timeout stops waiting; retries with exponential backoff try again after growing delays.
> - **When to use:** Every external call. Without a timeout a hung server can freeze your app forever.

```python
import random
import time

import requests

RETRYABLE = {408, 429, 500, 502, 503, 504, 529}
MAX_ATTEMPTS = 5


def get_with_retry(url: str) -> requests.Response:
    """GET with exponential backoff on retryable errors."""
    for attempt in range(MAX_ATTEMPTS):
        r = requests.get(url, timeout=10)
        if r.status_code not in RETRYABLE:
            return r
        # Honour the server's hint, otherwise back off 1s, 2s, 4s ... plus jitter
        wait = float(r.headers.get("retry-after", 2 ** attempt)) + random.random()
        time.sleep(wait)
    r.raise_for_status()
    return r
```

LLM SDKs (`anthropic`, `openai`) already retry 429 / 5xx automatically (`max_retries`). Library alternative: `tenacity`.

## 13. Rate Limits

> - **What:** The maximum number of requests (or tokens) you may send per time window.
> - **How:** The server counts your usage; over the limit it answers 429 with a `retry-after` header.
> - **When to use:** Batch jobs, many parallel LLM calls, public APIs.

- Read the limit headers (`x-ratelimit-remaining-requests`, `...-tokens`) and slow down before hitting 0.
- Limit concurrency: `asyncio.Semaphore(5)` allows only 5 requests at once.
- Use batch APIs for large offline jobs (cheaper, separate limits).
- Cache identical requests (see [40 - Redis](40_redis-queues.md)).

## 14. Pagination

> - **What:** Getting large result lists in pages.
> - **How:** Offset (`?page=2&limit=50`) or cursor (`?after=<id>`); the response tells you how to get the next page.
> - **When to use:** Any list endpoint that can return many items.

```python
items, cursor = [], None
while True:
    params = {"limit": 100}
    if cursor:
        params["after"] = cursor
    page = requests.get(url, params=params, timeout=10).json()
    items.extend(page["data"])
    if not page.get("has_more"):
        break
    cursor = page["data"][-1]["id"]
```

## 15. Streaming (SSE)

> - **What:** The server sends the response in small chunks as they are produced, over one open connection.
> - **How:** Server-Sent Events: `Content-Type: text/event-stream`, lines like `event: ...` and `data: {...}`, separated by blank lines.
> - **When to use:** LLM chat UIs (show tokens as they arrive), progress updates, long-running responses.

```text
event: content_block_delta
data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Hel"}}

event: content_block_delta
data: {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "lo"}}
```

```python
with httpx.stream("POST", url, json=payload, headers=headers, timeout=None) as r:
    for line in r.iter_lines():
        if line.startswith("data: "):
            chunk = json.loads(line[6:])
```

In practice use the SDK's streaming helper (see [26 - LLM APIs](26_llm-apis.md)); to stream from your own API, see `StreamingResponse` in [39 - FastAPI](39_fastapi.md).

## 16. Webhooks

> - **What:** Reverse API calls: a service sends an HTTP POST to YOUR URL when an event happens.
> - **How:** You register a URL; the service posts JSON; you verify its signature and reply 2xx quickly.
> - **When to use:** Payment confirmations, GitHub push events, finished batch jobs.

- Verify the signature header (HMAC with a shared secret) before trusting the payload.
- Respond fast (200) and do heavy work in a background job ([40 - Redis and Queues](40_redis-queues.md)).
- Make handlers idempotent: the same event may arrive twice.
- Local testing: expose your dev server with a tunnel (`ngrok http 8000`, VS Code port forwarding).

## 17. CORS

> - **What:** A browser security rule: a page from domain A may only call an API on domain B if B allows it.
> - **How:** The browser sends an `Origin` header (and sometimes an OPTIONS preflight); the API answers with `Access-Control-Allow-Origin`.
> - **When to use:** A frontend on `localhost:3000` calls your API on `localhost:8000` and the browser shows "blocked by CORS policy".

CORS only affects browsers; curl and Python are never blocked. Fix it on the **server** (FastAPI `CORSMiddleware`), not in the frontend.

## 18. HTTPS and TLS

> - **What:** HTTP encrypted with TLS so nobody in between can read or change the data.
> - **How:** The server presents a certificate proving its identity; client and server agree on encryption keys.
> - **When to use:** Always for anything public or carrying secrets. Setup: [43 - Nginx and HTTPS](43_nginx-https.md).

`SSL: CERTIFICATE_VERIFY_FAILED` means the certificate is not trusted (self-signed, corporate proxy, expired). Fix the certificate / CA bundle; do not disable verification (`verify=False`) in production.

## 19. REST vs GraphQL vs gRPC vs WebSocket

> - **What:** Other API styles you will meet.
> - **How:** Each trades simplicity for a specific strength.
> - **When to use:** Knowing which one a service uses and why.

| Style | How | Best for |
|---|---|---|
| REST | Resources + HTTP methods + JSON | Most public and internal APIs |
| GraphQL | One endpoint; client sends a query for exactly the fields it needs | Complex frontends with varied data needs |
| gRPC | Binary Protocol Buffers over HTTP/2, generated clients | Fast service-to-service calls |
| WebSocket | Persistent two-way connection | Chat, live collaboration, games, realtime voice |
| SSE | One-way server stream over HTTP | LLM token streaming, notifications |

## 20. Troubleshooting

| Problem | Fix |
|---|---|
| 401 Unauthorized | Key missing / wrong / expired; check header name (`x-api-key` vs `Authorization: Bearer`) and env var |
| 403 Forbidden | Key valid but lacks permission / wrong workspace / IP blocked |
| 404 Not Found | Typo in URL, missing `/v1`, wrong ID or model name |
| 405 Method Not Allowed | Wrong method (GET vs POST) |
| 415 / 400 with JSON body | Missing `Content-Type: application/json`; use `json=` in requests |
| 422 | Body shape does not match the schema; read the `detail` field |
| 429 | Slow down; respect `retry-after`; reduce concurrency |
| 5xx / 529 | Server side; retry with backoff; check the provider status page |
| Request hangs forever | No timeout set; add `timeout=` |
| `ConnectionError` / `ConnectTimeout` | Wrong host / port, server not running, firewall, VPN / proxy |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Update `certifi`, set corporate CA bundle (`REQUESTS_CA_BUNDLE`) |
| Works in curl, fails in browser | CORS; allow the origin on the server |
| JSON quotes break in PowerShell curl | Use `Invoke-RestMethod` with `ConvertTo-Json`, or `curl.exe` with escaped quotes |
