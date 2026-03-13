from __future__ import annotations

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "expl0v1n",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


def enqueue_vapt_scan(scan_id: str) -> None:
    celery_app.send_task("orchestrator.tasks.run_vapt_scan", args=[scan_id], queue="vapt")


def enqueue_hunting_pipeline(pipeline_id: str) -> None:
    celery_app.send_task(
        "orchestrator.tasks.run_hunting_pipeline", args=[pipeline_id], queue="hunting"
    )

