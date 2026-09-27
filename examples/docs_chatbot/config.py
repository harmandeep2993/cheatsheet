"""Chatbot settings loaded from environment variables (prefix CHATBOT_) or a .env file."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """All tunable values in one validated place; override with CHATBOT_<NAME> env vars."""

    model_config = SettingsConfigDict(env_prefix="CHATBOT_", env_file=".env", extra="ignore")

    llm_model: str = "claude-opus-5"
    max_tokens: int = Field(16000, gt=0)
    docs_dir: Path = PACKAGE_DIR / "docs"
    index_path: Path = PACKAGE_DIR / ".index" / "index.npz"
    chunk_chars: int = Field(1200, gt=100, description="About 300 tokens of English per chunk")
    chunk_overlap: int = Field(200, ge=0)
    top_k: int = Field(4, ge=1, le=20)
    min_score: float = Field(0.05, ge=0, le=1, description="Hits below this similarity are ignored")
