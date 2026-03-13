from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "production"
    log_level: str = "INFO"

    # Postgres (for context lookups)
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "expl0v1n"
    postgres_user: str = "expl0v1n_user"
    postgres_password: str = ""

    # Redis (rate limiting)
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""

    # LLM backend
    ai_provider: str = "openai_compatible"
    ai_api_url: AnyHttpUrl = "https://api.openai.com/v1"
    ai_api_key: str | None = None
    ai_model: str = "gpt-4o-mini"
    ai_max_tokens: int = 2048
    ai_temperature: float = 0.3
    ai_rate_limit_per_minute: int = 20

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

