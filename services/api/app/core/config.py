from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    environment: str = "production"
    log_level: str = "INFO"

    public_base_url: AnyHttpUrl = "http://localhost:3000"

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "expl0v1n"
    postgres_user: str = "expl0v1n"
    postgres_password: str = "change-me"

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0

    cors_allow_origins: str = "http://localhost:3000"

    jwt_issuer: str = "expl0v1n"
    jwt_audience: str = "expl0v1n-ui"
    jwt_access_ttl_seconds: int = 900
    jwt_refresh_ttl_seconds: int = 1209600
    jwt_secret: str = "change-me"

    api_rate_limit_per_minute: int = 120

    allow_public_targets: bool = False
    allowed_root_domains: str = "example.com,example.org"
    allowed_cidrs: str = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

    max_cpu_percent: int = 80
    min_free_mem_mb: int = 2048
    openvas_max_concurrent_scans: int = 1

    default_admin_email: str = "admin@local"
    default_admin_password: str = "change-me"

    reports_dir: str = "/data/reports"

    telegram_enabled: bool = False
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    ai_enabled: bool = False
    ai_provider: str = "openai_compatible"
    ai_base_url: AnyHttpUrl = "https://api.openai.com/v1"
    ai_api_key: str | None = None
    ai_model: str = "gpt-4.1-mini"
    ai_max_reqs_per_minute: int = 30

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()

