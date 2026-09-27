# Build from the examples/ folder:
#   docker build -f docs_chatbot/Dockerfile -t docs-chatbot .
#   docker run --rm -p 8000:8000 -e ANTHROPIC_API_KEY docs-chatbot
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Dependencies first so this layer is cached when only code changes
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY docs_chatbot/ docs_chatbot/

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "docs_chatbot.api:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
