from __future__ import annotations

import asyncio

from celery import Celery
from sqlalchemy import select

from app.config import settings
from app.db import SessionLocal
from app.models import NotificationConfig
from app.telegram import send_message


celery_app = Celery(
    "expl0v1n_notifications",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


def _get_telegram_config(user_id: int) -> tuple[bool, str | None, str | None]:
    db = SessionLocal()
    try:
        row = db.execute(select(NotificationConfig).where(NotificationConfig.user_id == user_id)).scalar_one_or_none()
        if row and row.enabled and row.provider == "telegram":
            return True, row.bot_token, row.chat_id
        return settings.telegram_enabled, settings.telegram_bot_token, settings.telegram_chat_id
    finally:
        db.close()


@celery_app.task(name="notifications.send_test")
def send_test(user_id: int) -> dict:
    enabled, bot_token, chat_id = _get_telegram_config(user_id=user_id)
    if not enabled or not bot_token or not chat_id:
        return {"status": "skipped", "reason": "telegram_not_configured"}

    text = "Expl0V1N: Test notification"
    asyncio.run(send_message(bot_token=bot_token, chat_id=chat_id, text=text))
    return {"status": "sent"}


@celery_app.task(name="notifications.send")
def send(user_id: int, text: str) -> dict:
    enabled, bot_token, chat_id = _get_telegram_config(user_id=user_id)
    if not enabled or not bot_token or not chat_id:
        return {"status": "skipped", "reason": "telegram_not_configured"}

    asyncio.run(send_message(bot_token=bot_token, chat_id=chat_id, text=text))
    return {"status": "sent"}
