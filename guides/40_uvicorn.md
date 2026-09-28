# 40 - Uvicorn (ASGI Server)

<!-- nav:start -->
**Previous:** [39 - FastAPI](39_fastapi.md) | **Index:** [All guides](../README.md) | **Next:** [41 - Redis, Caching and Task Queues](41_redis-queues.md)
<!-- nav:end -->

Quick reference for Uvicorn, the server that runs FastAPI and other async Python web apps: ASGI, running in development and production, workers, Gunicorn, proxies, HTTPS, timeouts, logging, Docker and systemd.

> **Last verified:** 2026-09-27. For newer changes, check the Official docs links in the Introduction.

## Introduction

### What is Uvicorn?

Your FastAPI code defines **what** should happen for each request (`@app.get("/items")`), but it does not listen on a network port or speak HTTP by itself. **Uvicorn** is the **server** that does that: it opens a port, accepts connections, parses raw HTTP bytes into requests, passes each one to your app through a standard interface called **ASGI**, and sends your app's response back to the client. It is built on `asyncio`, so one Uvicorn process can handle many connections at once while your async code waits on databases or LLM APIs.

### Mental model: the restaurant

```text
 CLIENTS                      UVICORN (the waiter / front of house)          YOUR APP (the kitchen)
 browser, curl, frontend      - listens on host:port                         FastAPI / Starlette
          |                   - accepts TCP connections                      - routes, validation (Pydantic)
          |  HTTP request     - parses HTTP, WebSockets                      - business logic, LLM calls
          +-----------------> - event loop juggles many clients    ASGI     - returns a response
                              - calls  app(scope, receive, send) ---------->
          <-----------------  - writes the HTTP response back   <----------
             HTTP response    - logging, timeouts, keep-alive, shutdown

 PRODUCTION SHAPE
 internet -> Nginx / cloud load balancer (HTTPS) -> Uvicorn workers (N processes) -> your app
            [44 Nginx]                              [40 this guide]                 [39 FastAPI]
```

- **ASGI** (Asynchronous Server Gateway Interface) is the contract between server and app: the server calls `app(scope, receive, send)`. Any ASGI server can run any ASGI app (FastAPI, Starlette, Django async, Quart ...).
- **Workers** are separate processes, each running its own copy of your app and event loop. More workers = more CPU cores used.
- The older standard, **WSGI** (Flask, classic Django with Gunicorn), handles one request per thread at a time; ASGI adds async and WebSockets.

### Why learn it?

- **Every FastAPI app runs on it** (`fastapi dev` / `fastapi run` use Uvicorn under the hood).
- **Production settings matter**: workers, timeouts, proxy headers and graceful shutdown decide reliability and correct client IPs / HTTPS detection.
- **Debugging**: "Error loading ASGI app", "address already in use", 502s behind Nginx and streaming problems are usually server settings, not your code.

### Key terms

| Term | Meaning |
|---|---|
| ASGI | Async interface between Python web servers and apps |
| WSGI | Older sync interface (Flask, classic Django) |
| ASGI app | Object the server calls (your `app = FastAPI()`) |
| App string `module:attribute` | Where Uvicorn finds the app, e.g. `app.main:app` |
| Event loop | asyncio scheduler handling many connections in one process ([13](13_async-python.md)) |
| Worker | Separate process running the app; one per CPU core is a common start |
| Reload | Restart automatically on code changes (development only) |
| Lifespan | Startup / shutdown events of the app (load models, open pools) |
| Keep-alive | Reusing one TCP connection for several requests |
| Graceful shutdown | Finish in-flight requests before exiting |
| Proxy headers | `X-Forwarded-For` / `X-Forwarded-Proto` set by a reverse proxy |
| uvloop / httptools | Faster event loop and HTTP parser (included in `uvicorn[standard]`) |

**Where it fits:** runs apps from [39 - FastAPI](39_fastapi.md) that validate data with [12 - Pydantic](12_pydantic.md) and use [13 - Async Python](13_async-python.md); sits behind [44 - Nginx and HTTPS](44_nginx-https.md) or a cloud load balancer ([47 - Azure](47_azure.md)); packaged with [42 - Docker](42_docker.md); protocol basics in [08 - HTTP and APIs](08_http-apis.md).

### Official docs

Where to read the latest, authoritative documentation:

| Resource | Link |
|---|---|
| Uvicorn documentation | https://uvicorn.dev/ |
| Uvicorn settings reference | https://uvicorn.dev/settings/ |
| Uvicorn deployment guide | https://uvicorn.dev/deployment/ |
| Uvicorn on GitHub | https://github.com/Kludex/uvicorn |
| ASGI specification | https://asgi.readthedocs.io/ |
| FastAPI: deployment concepts | https://fastapi.tiangolo.com/deployment/ |
| Gunicorn | https://gunicorn.org/ |

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install](#1-install)
2. [Run an App](#2-run-an-app)
3. [The App String and App Factory](#3-the-app-string-and-app-factory)
4. [Run from Python Code](#4-run-from-python-code)
5. [Development: Auto-Reload](#5-development-auto-reload)
6. [Host, Port and Sockets](#6-host-port-and-sockets)
7. [Workers and Concurrency](#7-workers-and-concurrency)
8. [Gunicorn with Uvicorn Workers](#8-gunicorn-with-uvicorn-workers)
9. [fastapi dev / fastapi run vs uvicorn](#9-fastapi-dev--fastapi-run-vs-uvicorn)
10. [Configuration via Environment Variables](#10-configuration-via-environment-variables)
11. [Logging](#11-logging)
12. [Behind a Reverse Proxy](#12-behind-a-reverse-proxy)
13. [HTTPS Directly in Uvicorn](#13-https-directly-in-uvicorn)
14. [Timeouts, Limits and Graceful Shutdown](#14-timeouts-limits-and-graceful-shutdown)
15. [Lifespan (Startup and Shutdown)](#15-lifespan-startup-and-shutdown)
16. [Streaming and WebSockets](#16-streaming-and-websockets)
17. [Performance Tips](#17-performance-tips)
18. [Uvicorn in Docker](#18-uvicorn-in-docker)
19. [Uvicorn as a systemd Service](#19-uvicorn-as-a-systemd-service)
20. [A Minimal ASGI App (How It Works Inside)](#20-a-minimal-asgi-app-how-it-works-inside)
21. [Other ASGI Servers](#21-other-asgi-servers)
22. [Production Checklist](#22-production-checklist)
23. [Troubleshooting](#23-troubleshooting)
24. [Try It](#24-try-it)

---

## 0. Flags and Parameters

> The Uvicorn command-line options. `uvicorn <module:app> [options]`; every option also exists as a `uvicorn.run(...)` argument and most as `UVICORN_*` environment variables.
>
> Use this when you see `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers` and want to know what each part does.

```text
uvicorn  app.main:app  --host 0.0.0.0  --port 8000  --workers 4  --proxy-headers
|        |        |    |               |            |            |
|        |        |    |               |            |            +-- trust X-Forwarded-* headers from the proxy
|        |        |    |               |            +--------------- 4 processes (use more CPU cores)
|        |        |    |               +---------------------------- TCP port
|        |        |    +-------------------------------------------- listen on all interfaces (containers / VMs)
|        |        +------------------------------------------------- variable holding the ASGI app
|        +---------------------------------------------------------- Python module path (app/main.py)
+------------------------------------------------------------------- the server
```

| Flag | Default | Meaning |
|---|---|---|
| `--host` | `127.0.0.1` | Interface to bind; `0.0.0.0` = reachable from other machines / containers |
| `--port` | `8000` | TCP port |
| `--uds /tmp/app.sock` | | Bind to a Unix socket (Linux; for Nginx on the same host) |
| `--reload` | off | Restart on code changes (development only) |
| `--reload-dir src` | cwd | Folders to watch (repeatable) |
| `--reload-include` / `--reload-exclude` | | Glob patterns to watch / ignore (`*.yaml`, `tests/*`) |
| `--workers 4` | 1 | Number of worker processes (not with `--reload`) |
| `--loop` | `auto` | Event loop: `auto`, `asyncio`, `uvloop` |
| `--http` | `auto` | HTTP parser: `auto`, `h11`, `httptools` |
| `--ws` | `auto` | WebSocket implementation (`none` to disable) |
| `--lifespan` | `auto` | Run app startup / shutdown events: `auto`, `on`, `off` |
| `--env-file .env` | | Load environment variables from a file |
| `--app-dir src` | `.` | Folder to add to the import path |
| `--factory` | off | Treat the target as a function that returns the app |
| `--log-level` | `info` | `critical`, `error`, `warning`, `info`, `debug`, `trace` |
| `--log-config file` | | Logging config (JSON / YAML / ini) |
| `--no-access-log` | on | Disable per-request access log lines |
| `--use-colors` / `--no-use-colors` | auto | Coloured log output |
| `--proxy-headers` / `--no-proxy-headers` | on | Read client IP / scheme from `X-Forwarded-*` |
| `--forwarded-allow-ips` | `127.0.0.1` | Which proxy IPs to trust (`*` = all, only in trusted networks) |
| `--root-path /api` | | App is served under a URL prefix by the proxy |
| `--limit-concurrency N` | | Max concurrent connections / tasks before returning 503 |
| `--limit-max-requests N` | | Restart a worker after N requests (mitigates memory leaks) |
| `--backlog` | 2048 | Max queued connections waiting to be accepted |
| `--timeout-keep-alive` | 5 | Seconds to keep an idle connection open |
| `--timeout-graceful-shutdown N` | | Max seconds to wait for in-flight requests on shutdown |
| `--ssl-keyfile` / `--ssl-certfile` | | Serve HTTPS directly |
| `--header "Name:Value"` | | Add a custom header to all responses |
| `--server-header` / `--no-server-header` | on | Send the `server: uvicorn` header |

---

## 1. Install

> Installing Uvicorn with or without the fast extras. `uvicorn[standard]` adds uvloop (faster event loop, not on Windows), httptools (fast HTTP parser), WebSockets, file watching for reload and `.env` support.
>
> Use it in every FastAPI / ASGI project. `fastapi[standard]` already includes it.

```powershell
pip install "uvicorn[standard]"           # recommended
uv add "uvicorn[standard]"                # with uv
pip install uvicorn                       # minimal (pure Python parts only)
uvicorn --version
```

## 2. Run an App

> Starting the server for your app. Point Uvicorn at `module:variable`; it imports the module and serves the ASGI app it finds.
>
> Use it for local development and simple deployments.

```python
# main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}
```

```powershell
uvicorn main:app                          # http://127.0.0.1:8000
uvicorn main:app --reload                 # development with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8080
python -m uvicorn main:app --reload       # same, guaranteed to use the active venv's Python
```

Stop with `Ctrl+C`. Open `http://127.0.0.1:8000/docs` for FastAPI's interactive docs.

## 3. The App String and App Factory

> How Uvicorn finds your app object. `package.module:attribute`, resolved from the current folder (or `--app-dir`); with `--factory`, the attribute is a function that builds the app.
>
> Use it for projects with a package layout; apps that need configuration at creation time (tests, several environments).

| Project layout | Command |
|---|---|
| `main.py` with `app = FastAPI()` | `uvicorn main:app` |
| `app/main.py` (package with `__init__.py`) | `uvicorn app.main:app` |
| `src/myapi/main.py` | `uvicorn myapi.main:app --app-dir src` |
| Variable named `api` instead of `app` | `uvicorn main:api` |

```python
# app/main.py - factory pattern
from fastapi import FastAPI


def create_app() -> FastAPI:
    """Build the application (settings, routers, middleware)."""
    app = FastAPI(title="Sales API")
    app.include_router(items.router)
    return app
```

```powershell
uvicorn app.main:create_app --factory --reload
```

## 4. Run from Python Code

> Starting Uvicorn inside a Python script. `uvicorn.run(...)` takes the same options as the CLI; pass the app as an import string to enable reload / workers.
>
> Use it for `python main.py` convenience, debugging in VS Code, embedding the server in a tool.

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
```

`uvicorn.run(app)` with the app object works too, but `reload` and `workers` require the import string. For VS Code debugging, see the launch configuration in [05 - VS Code](05_vscode.md) section 12.

## 5. Development: Auto-Reload

> Restarting the server automatically when you save a file. A watcher process monitors files and restarts the worker on changes.
>
> Use it for local development only. Never in production (slower, single process, watches the file system).

```powershell
uvicorn app.main:app --reload
uvicorn app.main:app --reload --reload-dir app --reload-dir prompts
uvicorn app.main:app --reload --reload-include "*.yaml" --reload-exclude "tests/*"
```

Large folders (`.venv`, `data/`, `node_modules/`) in the watch path make reload slow; restrict with `--reload-dir`.

## 6. Host, Port and Sockets

> Where the server listens. `127.0.0.1` accepts only local connections; `0.0.0.0` accepts from any network interface; a Unix socket is a file-based connection for a proxy on the same machine.
>
> Use it for `127.0.0.1` on laptops and behind a local Nginx; `0.0.0.0` inside Docker containers and when a load balancer connects over the network.

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000     # local only (safe default)
uvicorn app.main:app --host 0.0.0.0 --port 8000       # all interfaces (containers)
uvicorn app.main:app --uds /run/api.sock              # Unix socket (Linux, behind Nginx)
```

A server on `0.0.0.0` on a VM is reachable from the internet if the firewall allows the port: put a proxy with HTTPS in front ([44](44_nginx-https.md)).

## 7. Workers and Concurrency

> How Uvicorn handles many requests, and when to add processes. One worker = one process with one event loop. Async endpoints share it (thousands of waiting requests are fine); CPU-heavy or blocking code blocks it. More workers use more CPU cores, each with its own memory.
>
> Use it for production: start with 1 worker per CPU core (or let the platform scale containers instead).

```text
1 worker                              4 workers (--workers 4)
+----------------------------+        +--------+ +--------+ +--------+ +--------+
| event loop                 |        | loop 1 | | loop 2 | | loop 3 | | loop 4 |
|  req A waits for LLM  ...  |        +--------+ +--------+ +--------+ +--------+
|  req B waits for DB   ...  |        4x CPU cores, 4x memory (each loads the app / models)
|  req C being processed     |        OS distributes incoming connections
+----------------------------+
```

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

| Workload | Guidance |
|---|---|
| Mostly async I/O (LLM APIs, DB, HTTP calls) | Few workers go far; use async libraries ([13](13_async-python.md)) |
| Blocking libraries in `def` endpoints | FastAPI runs them in a thread pool; workers still help |
| CPU-heavy (pandas, local model inference) | More workers / processes, or move work to background jobs ([41](41_redis-queues.md)) |
| Large ML model loaded at startup | Each worker loads its own copy: memory = workers x model size |
| Containers on Kubernetes / Container Apps | Often 1 worker per container; scale the number of containers instead |

State in memory (dicts, caches) is **per worker**: use Redis / a database for anything shared ([41](41_redis-queues.md)).

## 8. Gunicorn with Uvicorn Workers

> Using Gunicorn as a process manager that runs Uvicorn worker processes. Gunicorn starts, monitors and restarts workers; each worker is a Uvicorn server (worker class from the `uvicorn-worker` package).
>
> Use it for Linux VMs where you want Gunicorn's mature process management, or platforms that expect Gunicorn (e.g. some App Service setups). Modern `uvicorn --workers` also restarts crashed workers, so plain Uvicorn is often enough.

```bash
pip install gunicorn uvicorn-worker
gunicorn app.main:app -k uvicorn_worker.UvicornWorker -w 4 -b 0.0.0.0:8000 \
  --timeout 120 --graceful-timeout 30 --access-logfile -
```

| Gunicorn flag | Meaning |
|---|---|
| `-k uvicorn_worker.UvicornWorker` | Worker class (older docs: `uvicorn.workers.UvicornWorker`, now deprecated) |
| `-w 4` | Number of workers |
| `-b host:port` | Bind address |
| `--timeout 120` | Kill a worker that is silent this long |
| `--max-requests 1000 --max-requests-jitter 100` | Recycle workers periodically |

Gunicorn does not run on Windows; use it on Linux / in containers.

## 9. fastapi dev / fastapi run vs uvicorn

> FastAPI's CLI commands that start Uvicorn for you. `fastapi dev` = Uvicorn with reload on 127.0.0.1; `fastapi run` = Uvicorn without reload on 0.0.0.0. Both auto-detect the app in the file.
>
> Use it for quick starts; use `uvicorn` directly when you need more options.

| Command | Equivalent |
|---|---|
| `fastapi dev main.py` | `uvicorn main:app --reload --host 127.0.0.1` |
| `fastapi run main.py` | `uvicorn main:app --host 0.0.0.0 --port 8000` |
| `fastapi run main.py --workers 4` | `uvicorn main:app --host 0.0.0.0 --workers 4` |

## 10. Configuration via Environment Variables

> Setting server options without changing the command. Uvicorn reads `UVICORN_*` variables for its options; `--env-file` loads a `.env` file into the environment (your app can read it too).
>
> Use it for containers and platforms where options come from environment settings.

```powershell
$env:UVICORN_HOST = "0.0.0.0"
$env:UVICORN_PORT = "8080"
$env:UVICORN_WORKERS = "2"
uvicorn app.main:app
```

```bash
uvicorn app.main:app --env-file .env          # needs python-dotenv (included in uvicorn[standard])
```

App configuration (API keys, model names) is best loaded by the app itself with `pydantic-settings` ([12 - Pydantic](12_pydantic.md) section 16).

## 11. Logging

> Server and access logs. Uvicorn uses Python's `logging` with loggers `uvicorn` (server), `uvicorn.error` and `uvicorn.access` (one line per request); configure via flags or a logging config file.
>
> Use it for debugging, production log formats (JSON), reducing noise.

```powershell
uvicorn app.main:app --log-level debug
uvicorn app.main:app --no-access-log                 # disable per-request lines (use your own middleware)
uvicorn app.main:app --log-config logging.yaml
```

```yaml
# logging.yaml - send uvicorn logs through one simple format
version: 1
disable_existing_loggers: false
formatters:
  default:
    format: "%(asctime)s %(levelname)s %(name)s: %(message)s"
handlers:
  console:
    class: logging.StreamHandler
    formatter: default
loggers:
  uvicorn:        {handlers: [console], level: INFO, propagate: false}
  uvicorn.access: {handlers: [console], level: INFO, propagate: false}
root:
  handlers: [console]
  level: INFO
```

Access log line: `INFO: 172.18.0.1:53422 - "POST /chat HTTP/1.1" 200 OK`. Your app's own logs: `logging.getLogger(__name__)` ([09](09_python-basics.md) section 25).

## 12. Behind a Reverse Proxy

> Running Uvicorn behind Nginx, a cloud load balancer or Kubernetes ingress. The proxy terminates HTTPS and forwards to Uvicorn; Uvicorn reads `X-Forwarded-For` / `X-Forwarded-Proto` (proxy headers) only from trusted IPs to get the real client IP and scheme.
>
> Use it in every production deployment.

```bash
# Nginx on the same machine
uvicorn app.main:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips="127.0.0.1"

# Inside a container behind a trusted load balancer / ingress
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"

# App served under /api by the proxy (so docs and redirects use the prefix)
uvicorn app.main:app --root-path /api
```

Without correct proxy settings: `request.client.host` shows the proxy's IP, and redirects / generated URLs may use `http` instead of `https`. Only trust `*` when Uvicorn is not reachable directly from the internet. Nginx side: [44 - Nginx and HTTPS](44_nginx-https.md) section 4.

## 13. HTTPS Directly in Uvicorn

> Serving TLS from Uvicorn without a proxy. Give it a key and certificate file.
>
> Use it for local HTTPS testing, internal services. For public sites prefer a proxy / platform that manages certificates ([44](44_nginx-https.md), [47](47_azure.md)).

```bash
uvicorn app.main:app --host 0.0.0.0 --port 443 \
  --ssl-keyfile /etc/ssl/private/key.pem --ssl-certfile /etc/ssl/certs/cert.pem
```

Local development certificates: `mkcert localhost` creates a trusted cert for your machine.

## 14. Timeouts, Limits and Graceful Shutdown

> Protecting the server and shutting down cleanly. Limit concurrent work, recycle workers, keep-alive timeouts, and give in-flight requests time to finish on shutdown (deployments, scale-down).
>
> Use it for production, especially with long LLM requests and streaming.

```bash
uvicorn app.main:app --host 0.0.0.0 --workers 4 \
  --limit-concurrency 200 \
  --limit-max-requests 10000 \
  --timeout-keep-alive 10 \
  --timeout-graceful-shutdown 30
```

| Setting | Why |
|---|---|
| `--limit-concurrency` | Return 503 instead of falling over when overloaded |
| `--limit-max-requests` | Restart workers periodically (memory leaks in libraries) |
| `--timeout-keep-alive` | Match or stay below the proxy / load balancer idle timeout to avoid 502s |
| `--timeout-graceful-shutdown` | Let running requests (e.g. LLM calls) finish during deploys |

Uvicorn has **no per-request timeout**: long requests run until done. Set timeouts on the proxy ([44](44_nginx-https.md)), on outgoing calls (LLM SDK `timeout`, [26](26_llm-apis.md)), or with `asyncio.timeout` in code ([13](13_async-python.md)); move very long work to background jobs ([41](41_redis-queues.md)).

## 15. Lifespan (Startup and Shutdown)

> Code that runs once per worker when it starts and stops. Uvicorn sends ASGI lifespan events; FastAPI runs your `lifespan` context manager ([39](39_fastapi.md) section 16).
>
> Use it for load ML models, open DB / HTTP client pools, warm caches; close them cleanly.

```python
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=30)     # one shared client per worker
    yield
    await app.state.http.aclose()


app = FastAPI(lifespan=lifespan)
```

With `--workers 4`, lifespan runs 4 times (once per process). `--lifespan off` disables it (for apps that do not support it).

## 16. Streaming and WebSockets

> Long-lived responses: LLM token streaming (SSE / chunked) and WebSockets. Uvicorn sends chunks as your app yields them; WebSockets need a WebSocket implementation (included in `uvicorn[standard]`).
>
> Use it for chat UIs, live progress ([38](38_ai-ui.md)).

- Install `uvicorn[standard]` (or `websockets`) for WebSocket support; otherwise you get "No supported WebSocket library detected".
- Behind Nginx, disable buffering and pass upgrade headers ([44](44_nginx-https.md) section 7).
- Streams hold a connection open: plan `--limit-concurrency` and graceful shutdown accordingly.

## 17. Performance Tips

> Getting the most from each worker. Fast event loop and parser, async libraries, the right number of workers, no blocking in async code.
>
> Use it for load testing and tuning.

- Use `uvicorn[standard]`: uvloop + httptools on Linux / macOS.
- Never block the event loop in `async def` (no `time.sleep`, `requests`, heavy pandas); use async clients or plain `def` endpoints ([13](13_async-python.md)).
- Reuse clients (HTTP, DB, LLM SDK) created at startup instead of per request.
- Turn off the access log in very high-traffic services and log in middleware instead.
- Load test before guessing: `locust`, `k6`, `hey`, `wrk`.

## 18. Uvicorn in Docker

> Running Uvicorn as the container's main process. Bind to `0.0.0.0`, use the exec form of `CMD` so Uvicorn receives stop signals (graceful shutdown), let the platform scale containers.
>
> Use it in every containerised API ([42 - Docker](42_docker.md)).

```dockerfile
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
```

- Exec form (`["uvicorn", ...]`) makes Uvicorn PID 1 so `docker stop` triggers graceful shutdown; the shell form (`CMD uvicorn ...`) can swallow signals.
- Use `--workers` only if the container has several CPUs and the platform does not scale containers for you.

## 19. Uvicorn as a systemd Service

> Keeping Uvicorn running on a Linux VM after logout, crashes and reboots. A systemd unit starts the venv's Uvicorn; Nginx proxies to it.
>
> Use it for deployments on a VM without Docker ([03 - Linux](03_linux.md), [48 - Azure VM](48_azure-vm-ollama.md)).

```ini
# /etc/systemd/system/api.service
[Unit]
Description=Sales API (Uvicorn)
After=network.target

[Service]
User=azureuser
WorkingDirectory=/home/azureuser/sales-api
EnvironmentFile=/home/azureuser/sales-api/.env
ExecStart=/home/azureuser/sales-api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2 --proxy-headers --timeout-graceful-shutdown 30
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload && sudo systemctl enable --now api
journalctl -u api -f
```

## 20. A Minimal ASGI App (How It Works Inside)

> The raw interface Uvicorn uses, without a framework. An ASGI app is an async callable receiving `scope` (request info), `receive` (read events) and `send` (write events).
>
> Use this when understanding what FastAPI does for you; writing middleware.

```python
# raw_app.py  ->  uvicorn raw_app:app
async def app(scope, receive, send):
    """Tiny ASGI app: answers every HTTP request with plain text."""
    if scope["type"] != "http":
        return
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [(b"content-type", b"text/plain")],
    })
    await send({"type": "http.response.body", "body": f"You requested {scope['path']}".encode()})
```

FastAPI builds on Starlette, which turns these events into `Request` / `Response` objects, routing, validation and docs.

## 21. Other ASGI Servers

> Alternatives to Uvicorn. All run standard ASGI apps; swap the command.
>
> Use this when specific needs such as HTTP/2 or HTTP/3, or maximum throughput.

| Server | Notes |
|---|---|
| Uvicorn | Default for FastAPI; simple, fast, widely used |
| Gunicorn + Uvicorn workers | Mature process management on Linux |
| Hypercorn | HTTP/2 and HTTP/3 support, Trio support |
| Granian | Rust-based, high performance, ASGI / WSGI / RSGI |
| Daphne | Django Channels' reference server |

## 22. Production Checklist

- [ ] No `--reload`; `uvicorn[standard]` installed
- [ ] Bound to `127.0.0.1` behind a local proxy, or `0.0.0.0` only inside a container / private network
- [ ] HTTPS terminated by a proxy / platform; `--proxy-headers` with correct `--forwarded-allow-ips`
- [ ] Workers sized to CPU and memory (models are loaded once per worker), or 1 worker per container with horizontal scaling
- [ ] `--timeout-graceful-shutdown` set; `--timeout-keep-alive` below the proxy idle timeout
- [ ] `--limit-concurrency` to shed load instead of crashing
- [ ] Health endpoint (`GET /health`) for probes ([45 - Kubernetes](45_kubernetes.md))
- [ ] Logs in a consistent format, request IDs, no secrets in logs
- [ ] Exec-form `CMD` in Docker / systemd with `Restart=always` on VMs

## 23. Troubleshooting

| Error / problem | Fix |
|---|---|
| `Error loading ASGI app. Could not import module "main"` | Run from the folder containing the module, use the full path (`app.main:app`), or `--app-dir src` |
| `Error loading ASGI app. Attribute "app" not found in module` | The variable has another name, or the app is created in a function (use `--factory`) |
| `[Errno 98] / [WinError 10048] address already in use` | Another server uses the port; stop it or use `--port 8001`; find it with `Get-NetTCPConnection -LocalPort 8000` ([02](02_terminal-powershell.md)) |
| Works on the VM, not reachable from outside / from Docker host | Bound to `127.0.0.1`; use `--host 0.0.0.0` (and publish the port / open the firewall) |
| `You must pass the application as an import string to enable 'reload' or 'workers'` | `uvicorn.run("app.main:app", reload=True)` instead of `uvicorn.run(app, ...)` |
| Reload does not pick up changes / is very slow | Restrict `--reload-dir`; exclude big folders; install `uvicorn[standard]` (watchfiles) |
| `No supported WebSocket library detected` | `pip install "uvicorn[standard]"` |
| Client IP is always the proxy's IP / wrong `http` scheme | `--proxy-headers --forwarded-allow-ips=<proxy ip>` |
| Random 502s behind a load balancer | Keep-alive mismatch: set `--timeout-keep-alive` higher than or aligned with the LB idle timeout per its docs, and check worker restarts |
| Server freezes under load | Blocking code in `async def`; CPU-heavy work; add workers or background jobs |
| Memory grows with `--workers` | Each worker loads the app / models; fewer workers or share models via a separate model server |
| Requests cut off during deploys | Add `--timeout-graceful-shutdown`; use exec-form `CMD` so signals reach Uvicorn |
| `uvloop` install fails on Windows | Expected; uvloop is Linux / macOS only; Uvicorn falls back to asyncio |

## 24. Try It

> Short exercises to practise this guide. Try each task yourself first, then open the solution.
>
> Use it right after reading the guide, or later as a quick self-test.

### Exercise 1: Focused reload

Run an app with auto-reload that only watches the `app/` folder.

<details markdown="1">
<summary>Solution</summary>

```bash
uvicorn app.main:app --reload --reload-dir app
```

</details>

### Exercise 2: Production command

Write the command for 4 workers behind a local Nginx, with real client IPs and 30 seconds of graceful shutdown.

<details markdown="1">
<summary>Solution</summary>

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4 \
  --proxy-headers --forwarded-allow-ips="127.0.0.1" --timeout-graceful-shutdown 30
```

</details>

### Exercise 3: Shared state surprise

A counter stored in a global dict shows different values on each request with `--workers 4`. Why, and what is the fix?

<details markdown="1">
<summary>Solution</summary>

Each worker is a separate process with its own memory, so each has its own dict. Store shared state in Redis or a database ([41](41_redis-queues.md)).

</details>

---

<!-- nav:start -->
**Previous:** [39 - FastAPI](39_fastapi.md) | **Index:** [All guides](../README.md) | **Next:** [41 - Redis, Caching and Task Queues](41_redis-queues.md)
<!-- nav:end -->
