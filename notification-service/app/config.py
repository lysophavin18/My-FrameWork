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

    celery_broker_url: str = env("CELERY_BROKER_URL", "")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", celery_broker_url)

    telegram_enabled: bool = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    telegram_bot_token: str | None = os.getenv("TELEGRAM_BOT_TOKEN") or None
    telegram_chat_id: str | None = os.getenv("TELEGRAM_CHAT_ID") or None

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()

