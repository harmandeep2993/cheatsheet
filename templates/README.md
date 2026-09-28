# Templates

Starting points you copy into your own projects. Both are tested in CI (`.github/workflows/templates.yml`), so they work as delivered.

| Folder | What it is | Guide |
|---|---|---|
| `fullstack-microservices/` | Runnable monorepo: two FastAPI services (documents and chat) in Docker, shared `libs/common`, React + Vite + TypeScript frontend, Nginx proxy, Postgres, Docker Compose for dev and production-like runs | [49 - Project Structure](../guides/49_project-structure.md) |
| `service-template/` | Copier template that generates one new service with the same layout into `fullstack-microservices/services/` | [50 - Project Templates](../guides/50_project-templates.md) |

## fullstack-microservices at a glance

```text
fullstack-microservices/
  compose.yaml, compose.dev.yaml   run everything (production-like / development)
  .env.example                     every setting with placeholders; copy to .env
  pyproject.toml, uv.lock          uv workspace: one lock file for all Python code
  libs/common/                     shared logging, request IDs, /health, base settings
  services/documents-service/      stores and searches documents (own Postgres database)
  services/chat-service/           answers questions from documents via an LLM
  frontend/                        React app, built into static files served by Nginx
  proxy/nginx.conf                 single public entry point on port 8080
  deploy/                          notes for Azure Container Apps and Kubernetes
```

## Quick start

```bash
cd templates/fullstack-microservices
uv sync --all-packages && uv run pytest          # tests, no Docker needed
cp .env.example .env && docker compose up --build   # whole system on http://localhost:8080

# Add a service from the Copier template
uvx copier copy ../service-template services/feedback-service
```

Each folder's own README has the details.
