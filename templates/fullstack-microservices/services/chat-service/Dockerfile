# Build from the repository root so the shared libs/ folder is inside the build context:
#   docker build -f services/chat-service/Dockerfile .
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /bin/uv

# Bytecode compiled at build time = faster start; copy mode because the cache is on another filesystem
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
WORKDIR /app

# 1) Third-party dependencies only. This layer is reused until uv.lock or a pyproject.toml changes.
COPY pyproject.toml uv.lock ./
COPY libs/common/pyproject.toml libs/common/pyproject.toml
COPY services/chat-service/pyproject.toml services/chat-service/pyproject.toml
# --frozen: trust uv.lock as is (the other services' folders are not copied, so it cannot be re-checked)
RUN uv sync --frozen --no-dev --package chat-service --no-install-workspace

# 2) Our own code: the shared library and this service, nothing from other services
COPY libs/common libs/common
COPY services/chat-service services/chat-service
RUN uv sync --frozen --no-dev --package chat-service --no-editable

ENV PATH="/app/.venv/bin:$PATH"
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "--factory", "chat_service.main:create_app", "--host", "0.0.0.0", "--port", "8000"]
