"""Settings for the documents service, read from DOCUMENTS_* environment variables."""

from pydantic_settings import SettingsConfigDict

from common import ServiceSettings


class Settings(ServiceSettings):
    """Documents service configuration. Compose sets DOCUMENTS_DATABASE_URL to the Postgres container."""

    model_config = SettingsConfigDict(env_prefix="DOCUMENTS_")

    # SQLite by default so the service also runs with plain `uv run` and no database container
    database_url: str = "sqlite:///./documents.db"
