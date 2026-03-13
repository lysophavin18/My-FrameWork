"""Expl0V1N Backend — Application Configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "Expl0V1N"
    app_env: str = "production"
    debug: bool = False
    secret_key: str = "CHANGE_ME"
    allowed_hosts: str = "localhost,127.0.0.1"

    # Database
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "expl0v1n"
    postgres_user: str = "expl0v1n_user"
    postgres_password: str = ""

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = ""

    # JWT
    jwt_secret_key: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Admin
    admin_email: str = "admin@expl0v1n.local"
    admin_password: str = "ChangeMeOnFirstLogin!"
    admin_username: str = "admin"

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"

    # Scan
    scan_cpu_threshold: int = 80
    scan_ram_threshold: int = 85

    # Scope enforcement (safe-by-default)
    allow_public_targets: bool = False
    allowed_root_domains: str = "example.com,example.org"
    allowed_cidrs: str = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Logging
    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
