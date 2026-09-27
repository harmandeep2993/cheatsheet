"""Settings for the chat service, read from CHAT_* environment variables (plus ANTHROPIC_API_KEY)."""

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict

from common import ServiceSettings


class Settings(ServiceSettings):
    """Chat service configuration. In Compose, CHAT_DOCUMENTS_URL points at the documents-service container."""

    # populate_by_name lets tests pass anthropic_api_key=... even though the env var name differs
    model_config = SettingsConfigDict(env_prefix="CHAT_", populate_by_name=True)

    documents_url: str = "http://localhost:8001"
    request_timeout_seconds: float = 5.0
    max_sources: int = 3
    model: str = "claude-opus-5"
    # The standard variable name, not CHAT_ prefixed; without it the service uses a fake offline LLM
    anthropic_api_key: SecretStr | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")

    @field_validator("anthropic_api_key", mode="before")
    @classmethod
    def _blank_key_means_none(cls, value: object) -> object:
        """Compose passes ANTHROPIC_API_KEY="" when the variable is unset; treat that as "no key"."""
        if isinstance(value, str) and not value.strip():
            return None
        return value
