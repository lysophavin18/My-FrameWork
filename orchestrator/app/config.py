from __future__ import annotations

import os


def env(key: str, default: str | None = None) -> str:
    v = os.getenv(key)
    if v is None or v == "":
        if default is None:
            raise RuntimeError(f"Missing required env var: {key}")
        return default
    return v


class Settings:
    postgres_host: str = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "expl0v1n")
    postgres_user: str = os.getenv("POSTGRES_USER", "expl0v1n_user")
    postgres_password: str = env("POSTGRES_PASSWORD", "")

    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = env("REDIS_PASSWORD", "")

    celery_broker_url: str = os.getenv("CELERY_BROKER_URL") or f"redis://:{redis_password}@{redis_host}:{redis_port}/0"
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND") or f"redis://:{redis_password}@{redis_host}:{redis_port}/1"

    scan_cpu_threshold: int = int(os.getenv("SCAN_CPU_THRESHOLD", "80"))
    scan_ram_threshold: int = int(os.getenv("SCAN_RAM_THRESHOLD", "85"))
    scan_timeout_seconds: int = int(os.getenv("SCAN_TIMEOUT_SECONDS", "3600"))

    openvas_max_concurrent_scans: int = int(os.getenv("OPENVAS_MAX_CONCURRENT_SCANS", "1"))

    results_dir: str = os.getenv("RESULTS_DIR", "/app/results")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"


settings = Settings()

