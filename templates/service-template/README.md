# Service Template (Copier)

Generates a new FastAPI service with the same layout as the services in `templates/fullstack-microservices`: app factory, settings with its own prefix, routes / services layers, health endpoint, shared logging, Dockerfile and tests. The guide is `guides/50_project-templates.md` in the pocket guide.

## Use it

From the root of `templates/fullstack-microservices` (or your copy of it):

```bash
uvx copier copy ../service-template services/feedback-service
# or without questions:
uvx copier copy ../service-template services/feedback-service --data service_name=feedback --defaults

uv lock && uv sync --all-packages
uv run pytest services/feedback-service
```

Copier prints the remaining manual steps (Compose, proxy, CI) after generating.

## Questions

| Question | Example | Used for |
|---|---|---|
| `service_name` | `feedback` | Folder `feedback-service`, package `feedback_service`, env prefix `FEEDBACK_`, URL `/api/feedback/` |
| `description` | `Stores thumbs up / down` | `pyproject.toml` and module docstring |
| `port` | `8000` | Port inside the container |

## Layout

```text
copier.yml                         questions, derived values, message after copy
{{_copier_conf.answers_file}}.jinja   writes .copier-answers.yml (needed by copier update)
pyproject.toml.jinja  Dockerfile.jinja
src/{{package_name}}/              becomes src/feedback_service/
tests/test_{{service_name}}_api.py.jinja
```

Files ending in `.jinja` are rendered (placeholders filled in) and lose the suffix; `{{ ... }}` in file and folder names is replaced too.
