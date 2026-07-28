from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env lives at the repo root, not inside backend/ — resolve it relative to
# this file so config loads correctly regardless of the process's cwd.
_REPO_ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_REPO_ROOT_ENV_FILE, extra="ignore")

    anthropic_api_key: str
    tavily_api_key: str
    oxylabs_username: str
    oxylabs_password: str

    llm_model: str = "anthropic:claude-sonnet-5"

    oxylabs_timeout_seconds: float = 15.0
    oxylabs_max_retries: int = 3

    max_search_calls_per_request: int = 3
    max_product_detail_lookups: int = 5
    default_marketplace_domain: str = "com"

    analysis_rate_limit: str = "10/minute"

    # Defaults to a local SQLite file — zero setup for local dev. Once
    # Supabase/Postgres is provisioned, set POSTGRES_URI (already reserved
    # in .env.example) to a real postgresql+asyncpg://... URL; `asyncpg`
    # will need to be added as a dependency at that point (uv add asyncpg).
    database_url: str = Field(
        default="sqlite+aiosqlite:///./marketpulse.db",
        validation_alias=AliasChoices("DATABASE_URL", "POSTGRES_URI"),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
