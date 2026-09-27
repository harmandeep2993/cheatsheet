# 17 - FastAPI

Quick reference for building Python web APIs with FastAPI: routes, validation, dependencies, testing and deployment.

## Introduction

### What is FastAPI?

FastAPI is a modern Python framework for building **web APIs**: programs that other programs talk to over HTTP. A client (web page, mobile app, another service, or `curl`) sends a request such as `POST /predict` with JSON data, and your FastAPI code returns a JSON response. FastAPI uses Python **type hints** and **Pydantic** models to validate incoming data automatically and to generate interactive documentation at `/docs`.

### Why use it?

- **Fast to write**: define a function, add a decorator, done.
- **Automatic validation**: wrong or missing input gets a clear 422 error without extra code.
- **Automatic docs**: Swagger UI at `/docs` to explore and test every endpoint in the browser.
- **High performance**: built on Starlette and async I/O; one of the fastest Python frameworks.
- **Editor support**: type hints give autocomplete and catch mistakes early.
- **Perfect for ML and data**: wrap a scikit-learn model or an LLM in an API in minutes.

### How a request flows

```text
Client (browser, app, curl)
   | HTTP request: POST /predict  {"age": 42, ...}
   v
Uvicorn (server) -> FastAPI (routing) -> validation (Pydantic) -> your function
   ^                                                                  |
   +--------------- HTTP response: 200 {"churn": false} <-------------+
```

### Key terms

| Term | Meaning |
|---|---|
| API | Interface that lets programs talk to each other |
| Endpoint / route | A URL + method your API answers (`GET /items`) |
| HTTP method | The action: GET read, POST create, PUT/PATCH update, DELETE remove |
| Status code | Result number: 200 OK, 404 not found, 422 invalid input |
| JSON | Text format for data sent and received |
| Pydantic model | Class that defines and validates data shape |
| ASGI server (Uvicorn) | The program that runs your app and handles connections |
| Dependency injection | FastAPI passes shared things (DB, settings) into endpoints via `Depends` |

**Where it fits:** serves models from [16 - Scikit-learn](16_scikit-learn.md) or Ollama ([19 - Azure VM](19_azure-vm-ollama.md)); ship it with [18 - Docker](18_docker.md).

---

## Contents

0. [Flags and Parameters](#0-flags-and-parameters)
1. [Install](#1-install)
2. [Minimal App](#2-minimal-app)
3. [Run the Server](#3-run-the-server)
4. [Interactive Docs](#4-interactive-docs)
5. [HTTP Methods and Status Codes](#5-http-methods-and-status-codes)
6. [Path Parameters](#6-path-parameters)
7. [Query Parameters](#7-query-parameters)
8. [Request Body (Pydantic Models)](#8-request-body-pydantic-models)
9. [Validation Rules](#9-validation-rules)
10. [Response Models](#10-response-models)
11. [Errors (HTTPException)](#11-errors-httpexception)
12. [Dependencies (Depends)](#12-dependencies-depends)
13. [Settings and Environment Variables](#13-settings-and-environment-variables)
14. [Project Structure and Routers](#14-project-structure-and-routers)
15. [async def vs def](#15-async-def-vs-def)
16. [Startup and Shutdown (Lifespan)](#16-startup-and-shutdown-lifespan)
17. [CORS and Middleware](#17-cors-and-middleware)
18. [Background Tasks](#18-background-tasks)
19. [File Uploads and Forms](#19-file-uploads-and-forms)
20. [Headers, Cookies and API Keys](#20-headers-cookies-and-api-keys)
21. [Testing](#21-testing)
22. [Call the API](#22-call-the-api)
23. [Example: Serve an ML Model](#23-example-serve-an-ml-model)
24. [Example: Proxy to Ollama](#24-example-proxy-to-ollama)
25. [Deploy (Docker)](#25-deploy-docker)
26. [Troubleshooting](#26-troubleshooting)

---

## 0. Flags and Parameters

> - **What:** The meaning of the server commands and the most common FastAPI parameters.
> - **How:** Server flags control how the app runs; decorator and function parameters control each endpoint.
> - **When to use:** You see `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` and want to know what each part does.

```text
uvicorn  app.main:app  --reload  --host 0.0.0.0  --port 8000
|        |        |    |         |               |
|        |        |    |         |               +-- port to listen on
|        |        |    |         +------------------ 0.0.0.0 = reachable from other machines / containers
|        |        |    +---------------------------- restart when code changes (development only)
|        |        +--------------------------------- variable name of the FastAPI object
|        +------------------------------------------ module path: app/main.py
+--------------------------------------------------- ASGI server that runs the app
```

| Command | Flag | Meaning |
|---|---|---|
| `uvicorn` / `fastapi` | `--reload` | Restart on code changes (never in production) |
| `uvicorn` / `fastapi` | `--host` | `127.0.0.1` = only this machine (default), `0.0.0.0` = all interfaces |
| `uvicorn` / `fastapi` | `--port` | Port (default 8000) |
| `uvicorn` / `fastapi` | `--workers 4` | Number of processes (production, uses more CPU cores) |
| `uvicorn` | `--env-file .env` | Load environment variables from a file |
| `uvicorn` | `--log-level debug` | More detailed logs |
| `fastapi dev` | | Development server: reload on, host 127.0.0.1 |
| `fastapi run` | | Production server: reload off, host 0.0.0.0 |

```text
@app.get("/items/{item_id}", response_model=Item, status_code=200, tags=["items"])
def read_item(item_id: int, q: str | None = None, db = Depends(get_db)):
              |             |                    |
              |             |                    +-- dependency: FastAPI calls get_db() and passes the result
              |             +----------------------- query parameter (?q=...), optional because default is None
              +------------------------------------- path parameter from {item_id}, converted to int
```

| Parameter | Where | Meaning |
|---|---|---|
| path string | `@app.get("/items/{item_id}")` | URL; `{name}` parts become path parameters |
| `response_model` | decorator | Pydantic model used to filter and document the response |
| `status_code` | decorator | HTTP status on success (`201` for created) |
| `tags` | decorator | Group endpoints in the docs |
| `summary`, `description` | decorator | Text in the docs |
| type hints | function args | Used to validate and convert input (`int`, `str`, `list[str]`, models) |
| default `= None` | function args | Makes a query parameter optional |
| `Depends(...)` | function args | Inject shared logic (db session, current user, settings) |

---

## 1. Install

> - **What:** FastAPI plus a server to run it.
> - **How:** `fastapi[standard]` includes uvicorn, the `fastapi` CLI and common extras.
> - **When to use:** Building an API for a web / mobile app, an ML model, or a service other programs call.

```powershell
pip install "fastapi[standard]"
uv add "fastapi[standard]"          # with uv
```

## 2. Minimal App

> - **What:** The smallest working API.
> - **How:** Create a `FastAPI()` object and decorate functions with the HTTP method and path.
> - **When to use:** Starting point for every project.

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="My API", version="0.1.0")


@app.get("/")
def root():
    """Health check."""
    return {"status": "ok"}


@app.get("/hello/{name}")
def hello(name: str):
    """Greet someone by name."""
    return {"message": f"Hello {name}"}
```

Return a dict, list, Pydantic model or plain value; FastAPI converts it to JSON.

## 3. Run the Server

> - **What:** Starting the app so it answers HTTP requests.
> - **How:** The ASGI server (uvicorn) imports your `app` object and listens on a port.
> - **When to use:** Development with reload; production with workers and no reload.

```powershell
fastapi dev main.py                         # development, http://127.0.0.1:8000
fastapi run main.py                         # production style
uvicorn main:app --reload                   # same as dev, with uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4   # production
```

Stop with `Ctrl+C`.

## 4. Interactive Docs

> - **What:** Automatically generated API documentation you can test in the browser.
> - **How:** FastAPI builds an OpenAPI schema from your routes and type hints.
> - **When to use:** Testing endpoints during development, sharing the API with frontend / other teams.

| URL | Shows |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger UI: click an endpoint -> **Try it out** -> **Execute** |
| `http://127.0.0.1:8000/redoc` | ReDoc: readable reference |
| `http://127.0.0.1:8000/openapi.json` | Raw schema (for generating clients) |

## 5. HTTP Methods and Status Codes

> - **What:** Which method to use for which action and what the response codes mean.
> - **How:** One decorator per method: `@app.get`, `.post`, `.put`, `.patch`, `.delete`.
> - **When to use:** Designing endpoints so clients know what each one does.

| Method | Purpose | Typical success code |
|---|---|---|
| `GET` | Read data | 200 OK |
| `POST` | Create / run an action | 201 Created (or 200) |
| `PUT` | Replace a resource | 200 OK |
| `PATCH` | Update part of a resource | 200 OK |
| `DELETE` | Delete | 204 No Content |

| Code | Meaning |
|---|---|
| 200 / 201 / 204 | OK / Created / No content |
| 400 | Bad request (your own check failed) |
| 401 / 403 | Not logged in / not allowed |
| 404 | Not found |
| 422 | Validation error (FastAPI: wrong or missing input) |
| 500 | Server error (bug / exception) |

```python
from fastapi import status

@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    ...

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    ...
```

## 6. Path Parameters

> - **What:** Values that are part of the URL path, like an ID.
> - **How:** Put `{name}` in the path and a function argument with the same name and a type.
> - **When to use:** Identifying one specific resource: `/users/42`, `/models/v2`.

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):              # "/users/abc" -> 422 error automatically
    return {"user_id": user_id}

from enum import Enum

class ModelName(str, Enum):
    small = "small"
    large = "large"

@app.get("/models/{name}")
def get_model(name: ModelName):          # only "small" or "large" allowed
    return {"model": name}
```

Order matters: define `/users/me` before `/users/{user_id}`.

## 7. Query Parameters

> - **What:** Optional values after `?` in the URL: `/items?skip=0&limit=10`.
> - **How:** Any function argument that is not in the path and not a model becomes a query parameter.
> - **When to use:** Filtering, sorting, pagination, search terms.

```python
@app.get("/items")
def list_items(skip: int = 0, limit: int = 10, q: str | None = None, active: bool = True):
    return {"skip": skip, "limit": limit, "q": q, "active": active}

# GET /items?skip=20&limit=5&q=lamp&active=false
```

- With a default: optional. Without a default: required.
- `bool` accepts `true/false`, `1/0`, `yes/no`.
- List: `tags: list[str] = Query(default=[])` -> `?tags=a&tags=b`.

## 8. Request Body (Pydantic Models)

> - **What:** JSON data sent by the client (usually with POST / PUT / PATCH).
> - **How:** Define a Pydantic `BaseModel`; use it as an argument type; FastAPI parses and validates the JSON.
> - **When to use:** Creating or updating resources, sending input for a prediction.

```python
from pydantic import BaseModel


class Item(BaseModel):
    """Item sent by the client."""

    name: str
    price: float
    tags: list[str] = []
    description: str | None = None


@app.post("/items", status_code=201)
def create_item(item: Item):
    data = item.model_dump()             # to dict
    return {"received": data, "price_with_tax": item.price * 1.19}
```

```json
{ "name": "Lamp", "price": 25.5, "tags": ["home"] }
```

Missing `name` or `"price": "abc"` -> automatic 422 response listing the problem.

## 9. Validation Rules

> - **What:** Extra rules on input values: ranges, lengths, patterns.
> - **How:** `Field()` in models; `Query()` / `Path()` for URL parameters; `Annotated` keeps it readable.
> - **When to use:** Rejecting bad input early (negative prices, empty names, huge limits).

```python
from typing import Annotated

from fastapi import Path, Query
from pydantic import BaseModel, EmailStr, Field, field_validator


class User(BaseModel):
    """New user registration."""

    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=0, le=120)                 # ge: >=, gt: >, le: <=, lt: <
    email: EmailStr                                # needs: pip install "pydantic[email]"
    zip_code: str = Field(pattern=r"^\d{5}$")

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip().title()


@app.get("/items/{item_id}")
def get_item(
    item_id: Annotated[int, Path(ge=1)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return {"item_id": item_id, "limit": limit}
```

## 10. Response Models

> - **What:** A model describing exactly what the endpoint returns.
> - **How:** `response_model=` (or the return type hint) filters out extra fields and documents the output.
> - **When to use:** Never leak internal fields (password hashes, internal IDs); give clients a stable contract.

```python
class UserIn(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    saved = {"id": 1, "email": user.email, "password": user.password}
    return saved                          # password is removed from the response
```

## 11. Errors (HTTPException)

> - **What:** Returning an error response with a status code and message.
> - **How:** `raise HTTPException(status_code=..., detail=...)`; FastAPI turns it into JSON.
> - **When to use:** Resource not found, not allowed, invalid business rule.

```python
from fastapi import HTTPException

ITEMS = {1: "Lamp"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, "name": ITEMS[item_id]}
```

Response: `404 {"detail": "Item not found"}`.

## 12. Dependencies (Depends)

> - **What:** Reusable pieces that endpoints need: DB session, current user, settings, pagination.
> - **How:** Write a function; add `param = Depends(func)`; FastAPI calls it for each request and passes the result.
> - **When to use:** The same code would otherwise repeat in many endpoints; also makes testing easy (override it).

```python
from typing import Annotated

from fastapi import Depends


def pagination(skip: int = 0, limit: int = 10):
    """Shared paging parameters."""
    return {"skip": skip, "limit": limit}


def get_db():
    """Open a DB session per request and always close it."""
    db = SessionLocal()
    try:
        yield db                     # code after yield runs when the request is done
    finally:
        db.close()


@app.get("/orders")
def list_orders(page: Annotated[dict, Depends(pagination)], db=Depends(get_db)):
    return db.query(Order).offset(page["skip"]).limit(page["limit"]).all()
```

## 13. Settings and Environment Variables

> - **What:** Configuration (URLs, keys, model names) read from environment variables / `.env`.
> - **How:** `pydantic-settings` reads variables into a typed settings class.
> - **When to use:** Anything that differs between laptop, test and production, and every secret.

```powershell
pip install pydantic-settings
```

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "My API"
    ollama_host: str = "http://localhost:11434"
    api_key: str                              # required: startup fails if missing


@lru_cache                                    # read the environment only once
def get_settings() -> Settings:
    return Settings()


@app.get("/info")
def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {"app": settings.app_name}
```

Keep secrets in `.env` (git-ignored); never hard-code them.

## 14. Project Structure and Routers

> - **What:** Splitting a growing API into files.
> - **How:** `APIRouter` groups related endpoints; `app.include_router` adds them under a prefix.
> - **When to use:** More than a handful of endpoints, or several resource types.

```text
app/
  __init__.py
  main.py              creates app, includes routers
  config.py            Settings
  dependencies.py      shared Depends functions
  routers/
    __init__.py
    items.py
    users.py
  schemas/             Pydantic models
  services/            business logic (routes only validate, call a service, return)
tests/
  test_items.py
```

```python
# app/routers/items.py
from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
def list_items():
    return []


# app/main.py
from fastapi import FastAPI

from app.routers import items, users

app = FastAPI()
app.include_router(items.router)
app.include_router(users.router)
```

Run: `uvicorn app.main:app --reload`.

## 15. async def vs def

> - **What:** Two ways to write endpoint functions.
> - **How:** `async def` runs on the event loop (use `await`); `def` runs in a thread pool.
> - **When to use:** `async def` when you call async libraries (`httpx`, async DB drivers); plain `def` for blocking code (pandas, scikit-learn, `requests`, most DB drivers).

```python
import httpx

@app.get("/weather")
async def weather():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.example.com/weather")
    return r.json()

@app.post("/predict")
def predict(data: Features):            # blocking ML code: plain def
    return {"y": model.predict(...)}
```

Never call blocking code (like `time.sleep` or `requests.get`) inside `async def`; it freezes the whole server.

## 16. Startup and Shutdown (Lifespan)

> - **What:** Code that runs once when the server starts and once when it stops.
> - **How:** An async context manager passed as `lifespan=`; code before `yield` = startup, after = shutdown.
> - **When to use:** Loading an ML model, opening connection pools, warming caches.

```python
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI

ml = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml["model"] = joblib.load("model.joblib")      # load once, not per request
    yield
    ml.clear()


app = FastAPI(lifespan=lifespan)
```

## 17. CORS and Middleware

> - **What:** Middleware runs around every request; CORS lets browsers on other domains call your API.
> - **How:** `app.add_middleware(...)`, or `@app.middleware("http")` for your own.
> - **When to use:** A frontend on `localhost:3000` calls your API on `localhost:8000` (browser shows a CORS error).

```python
import time

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],       # never "*" together with credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.3f}"
    return response
```

## 18. Background Tasks

> - **What:** Work that runs after the response is sent.
> - **How:** Add a `BackgroundTasks` parameter and schedule a function with `add_task`.
> - **When to use:** Sending emails, writing logs, small follow-up jobs the client should not wait for (use Celery / a queue for heavy jobs).

```python
from fastapi import BackgroundTasks


def write_log(message: str):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")


@app.post("/notify")
def notify(email: str, tasks: BackgroundTasks):
    tasks.add_task(write_log, f"notified {email}")
    return {"status": "queued"}
```

## 19. File Uploads and Forms

> - **What:** Receiving files and HTML form data.
> - **How:** `UploadFile` for files, `Form()` for form fields (needs `python-multipart`, included in `fastapi[standard]`).
> - **When to use:** Uploading CSVs for analysis, images for a model, login forms.

```python
import io

import pandas as pd
from fastapi import File, Form, UploadFile


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files allowed")
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    return {"rows": len(df), "columns": list(df.columns)}


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return {"user": username}
```

## 20. Headers, Cookies and API Keys

> - **What:** Reading request headers / cookies and protecting endpoints with a key.
> - **How:** `Header()` / `Cookie()` parameters; a dependency that checks the key and raises 401.
> - **When to use:** Simple machine-to-machine auth, reading `User-Agent`, custom headers. (For user logins, use OAuth2 / JWT.)

```python
from fastapi import Header, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")


def check_key(key: str = Security(api_key_header), settings: Settings = Depends(get_settings)):
    if key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/secure", dependencies=[Depends(check_key)])
def secure():
    return {"ok": True}


@app.get("/agent")
def agent(user_agent: str | None = Header(default=None)):
    return {"user_agent": user_agent}
```

## 21. Testing

> - **What:** Automated tests that call your endpoints without running a server.
> - **How:** `TestClient` sends requests directly to the app; run with pytest.
> - **When to use:** Every endpoint; run before each commit / in CI.

```python
# tests/test_main.py
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_invalid_item():
    r = client.post("/items", json={"name": "Lamp"})     # price missing
    assert r.status_code == 422


def test_with_override():
    app.dependency_overrides[get_settings] = lambda: Settings(api_key="test")
    ...
    app.dependency_overrides.clear()
```

```powershell
pip install pytest
pytest -q
```

## 22. Call the API

> - **What:** Sending requests to your API from the terminal or Python.
> - **How:** curl / PowerShell / requests / httpx with the method, URL, headers and JSON body.
> - **When to use:** Manual testing, scripts, other services calling yours.

```bash
curl http://127.0.0.1:8000/items?limit=5
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d '{"name": "Lamp", "price": 25}'
```

```powershell
Invoke-RestMethod http://127.0.0.1:8000/items
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/items `
  -ContentType "application/json" -Body '{"name": "Lamp", "price": 25}'
curl.exe -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Lamp\", \"price\": 25}"
```

```python
import requests

r = requests.post("http://127.0.0.1:8000/items", json={"name": "Lamp", "price": 25}, timeout=10)
r.raise_for_status()
r.json()
```

## 23. Example: Serve an ML Model

> - **What:** A prediction API for a scikit-learn pipeline.
> - **How:** Load the saved pipeline at startup, validate input with Pydantic, return the prediction.
> - **When to use:** Making a trained model available to apps and other services. Model training: [16 - Scikit-learn](16_scikit-learn.md).

```python
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

ml = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml["model"] = joblib.load("churn_model.joblib")
    yield
    ml.clear()


app = FastAPI(title="Churn API", lifespan=lifespan)


class Customer(BaseModel):
    """Input features for one customer."""

    age: int = Field(ge=18, le=100)
    monthly_spend: float = Field(ge=0)
    city: str
    segment: str


class Prediction(BaseModel):
    churn: bool
    probability: float


@app.post("/predict", response_model=Prediction)
def predict(customer: Customer):
    X = pd.DataFrame([customer.model_dump()])
    proba = float(ml["model"].predict_proba(X)[0, 1])
    return Prediction(churn=proba >= 0.5, probability=round(proba, 3))
```

## 24. Example: Proxy to Ollama

> - **What:** An API endpoint that forwards a prompt to an Ollama model.
> - **How:** Read `OLLAMA_HOST` from settings; call Ollama's chat API with the async client.
> - **When to use:** Putting your own API (auth, logging, prompt templates) in front of a local or VM-hosted LLM. VM setup: [19 - Azure VM + Linux + Ollama](19_azure-vm-ollama.md).

```python
import os

import ollama
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
client = ollama.AsyncClient(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))


class Ask(BaseModel):
    question: str


@app.post("/ask")
async def ask(body: Ask):
    resp = await client.chat(
        model=os.getenv("LLM_MODEL", "qwen3:4b"),
        messages=[{"role": "user", "content": body.question}],
        think=False,
    )
    return {"answer": resp["message"]["content"]}
```

## 25. Deploy (Docker)

> - **What:** Packaging the API as a container for any server or cloud.
> - **How:** Dockerfile installs dependencies, copies code, runs uvicorn on `0.0.0.0`.
> - **When to use:** Deploying to a VM, Azure Container Apps, App Service or Kubernetes. Details: [18 - Docker](18_docker.md).

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
```

```bash
docker build -t my-api:1.0 .
docker run -d -p 8000:8000 --env-file .env --name my-api my-api:1.0
```

Production checklist: no `--reload`, secrets from environment, `--workers` or several containers, HTTPS via a reverse proxy / cloud load balancer, health endpoint (`GET /`).

## 26. Troubleshooting

| Problem | Fix |
|---|---|
| `Error loading ASGI app. Could not import module "main"` | Run from the right folder; use the module path: `uvicorn app.main:app` |
| `Attribute "app" not found in module` | The FastAPI variable has another name; use `module:variable` |
| `422 Unprocessable Entity` | Input does not match types / rules; the response `detail` lists the field and reason |
| `address already in use` / port 8000 busy | Stop the other server, or `--port 8001`; find it with `Get-NetTCPConnection -LocalPort 8000` |
| Works locally, not reachable from Docker / VM | Start with `--host 0.0.0.0` and publish the port (`-p 8000:8000`) |
| Browser: `blocked by CORS policy` | Add `CORSMiddleware` with the frontend origin |
| Whole server freezes during a request | Blocking code inside `async def`; use plain `def` or async libraries |
| Route `/users/me` returns 422 | Defined after `/users/{user_id}`; move the fixed path first |
| `Form data requires "python-multipart"` | `pip install python-multipart` (or `fastapi[standard]`) |
| Settings / `.env` not loaded | Check `env_file` path and variable names; restart the server |
| Model loaded on every request (slow) | Load it once in `lifespan` |
