# Full-stack Microservices Starter

A small but complete starting point for **several Python services in Docker containers** plus a **separate React frontend**, all in one repository. The guide that explains every folder and decision is `49_project-structure.md` in the root of the pocket guide.

What it does: you add documents in the browser, then ask questions about them. `documents-service` stores and searches the documents; `chat-service` fetches the best matches and asks an LLM (Claude when `ANTHROPIC_API_KEY` is set, otherwise a built-in offline fake) to answer from them.

## Layout

```text
fullstack-microservices/
  compose.yaml            all containers, production-like (only the proxy publishes a port)
  compose.dev.yaml        dev overrides: code mounted from disk, auto reload, extra ports
  .env.example            every variable with placeholders; copy to .env (git-ignored)
  pyproject.toml          uv workspace root; uv.lock pins every Python dependency
  libs/common/            shared infrastructure: logging, request IDs, /health, base settings
  services/
    documents-service/    owns the documents database (Postgres in Compose, SQLite locally)
    chat-service/         calls documents-service over HTTP, then the LLM
  frontend/               React + Vite + TypeScript, built into static files served by Nginx
  proxy/nginx.conf        /api/documents/ and /api/chat/ to the services, everything else to the frontend
  deploy/                 notes for Azure Container Apps and Kubernetes
```

Inside each service:

```text
src/<service_name>/
  main.py          create_app(): middleware, routers, startup and shutdown
  config.py        Settings from environment variables (one prefix per service)
  api/routes.py    HTTP only: validate input, call the service layer, return
  services/        business logic
  repositories/    database access (documents-service)
  clients/         HTTP clients for other services (chat-service)
  schemas.py       request / response models (the API contract)
tests/             run without Docker, a database server or an API key
```

## Run the tests (no Docker needed)

```bash
uv sync --all-packages      # one virtual environment with every service and dev tools
uv run ruff check .
uv run pytest               # all services
uv run pytest services/chat-service   # one service
```

## Run the whole system with Docker

```bash
cp .env.example .env        # then edit .env: set DOCUMENTS_DB_PASSWORD (and optionally ANTHROPIC_API_KEY)
docker compose up --build
```

Open http://localhost:8080. Useful checks:

```bash
curl http://localhost:8080/api/documents/health
curl http://localhost:8080/api/chat/health
curl -X POST http://localhost:8080/api/documents/ -H "Content-Type: application/json" \
  -d '{"title": "Refunds", "content": "Refunds are paid within 5 days."}'
curl -X POST http://localhost:8080/api/chat/ask -H "Content-Type: application/json" \
  -d '{"question": "How long do refunds take?"}'
```

## Develop

```bash
# Backend with auto reload (code is mounted from your disk)
docker compose -f compose.yaml -f compose.dev.yaml up --build

# Frontend with hot reload, in a second terminal
cd frontend
npm install
npm run dev                 # http://localhost:5173, /api is forwarded to the proxy on 8080
```

Run one service directly on your machine, without Docker:

```bash
uv run --package documents-service uvicorn --factory documents_service.main:create_app --port 8001 --reload
```

## Add a new service

1. Copy `services/documents-service` to `services/<name>-service` and rename the package folder under `src/`.
2. Update its `pyproject.toml` (name, dependencies) and Dockerfile (package name, paths).
3. Run `uv lock` in the root so the new member is in `uv.lock`.
4. Add the service to `compose.yaml` and a `location /api/<name>/` block to `proxy/nginx.conf`.
5. Add it to the CI image matrix. Its tests run automatically (`testpaths` matches `services/*/tests`).

## Configuration

| Variable | Used by | Meaning |
|---|---|---|
| `DOCUMENTS_DB_PASSWORD` | Compose | Password of the documents Postgres database |
| `DOCUMENTS_DATABASE_URL` | documents-service | SQLAlchemy URL (Compose builds it from the password) |
| `CHAT_DOCUMENTS_URL` | chat-service | Base URL of documents-service |
| `CHAT_MAX_SOURCES` | chat-service | How many documents to send to the LLM |
| `CHAT_MODEL` | chat-service | Claude model name |
| `ANTHROPIC_API_KEY` | chat-service | Optional; without it the offline fake answers |
| `LOG_LEVEL` | Compose | Passed to both services as `<PREFIX>_LOG_LEVEL` |
