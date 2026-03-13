"""Task dispatcher sends work to Celery orchestrator queues."""

import os
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "expl0v1n_dispatcher",
    broker=settings.celery_broker_url,
    backend=os.getenv("CELERY_RESULT_BACKEND", settings.celery_broker_url),
)


def dispatch_vapt_scan(scan_id: int) -> None:
    celery_app.send_task("orchestrator.run_vapt_scan", args=[scan_id], queue="vapt")


def cancel_vapt_scan(scan_id: int) -> None:
    celery_app.send_task("orchestrator.cancel_vapt_scan", args=[scan_id], queue="vapt")


def dispatch_hunting_pipeline(session_id: int) -> None:
    celery_app.send_task("orchestrator.run_hunting_pipeline", args=[session_id], queue="hunting")


def cancel_hunting_pipeline(session_id: int) -> None:
    celery_app.send_task("orchestrator.cancel_hunting_pipeline", args=[session_id], queue="hunting")


def dispatch_test_notification(user_id: int) -> None:
    celery_app.send_task("notifications.send_test", args=[user_id], queue="default")
