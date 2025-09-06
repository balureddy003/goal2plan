from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment-driven kernel settings."""

    # General
    SEED: int = 42
    N_WORKERS: int = 1
    CPU_ONLY: bool = True

    # LLM provider
    LLM_PROVIDER: Literal["mock", "ollama", "lmstudio", "hf", "azure", "openai"] = "mock"

    # Provider-specific
    OLLAMA_BASE: Optional[str] = None
    OLLAMA_MODEL: str = "llama3"

    LMSTUDIO_BASE: Optional[str] = None
    LMSTUDIO_MODEL: str = "lmstudio-community/Qwen2-1.5B-Instruct-GGUF"

    HF_TOKEN: Optional[str] = None
    HF_MODEL: str = "gpt2"

    AZURE_BASE: Optional[str] = None
    AZURE_API_KEY: Optional[str] = None
    AZURE_MODEL: Optional[str] = None
    AZURE_API_VERSION: str = "2024-05-01-preview"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Singleton access to settings loaded from env/.env."""
    return Settings()  # type: ignore[call-arg]

