from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.hunting import HuntingPipeline, PipelineStep
from app.db.models.target import Target
from app.services.queue import enqueue_hunting_pipeline
from app.services.targets import enforce_scope, normalize_target


DEFAULT_PIPELINE_STEPS = ["subdomains", "live_hosts", "crawl", "screenshots", "nuclei"]


def create_pipeline(
    db: Session,
    *,
    root_domain: str,
    steps: list[str],
    options: dict,
    requested_by: uuid.UUID,
) -> HuntingPipeline:
    normalized = normalize_target(root_domain)
    if normalized.type != "domain":
        raise ValueError("root_domain_must_be_domain")

    enforce_scope(normalized)

    # Require explicit approval for public root domains via Targets table.
    if normalized.is_public:
        t = db.execute(
            select(Target).where(Target.type == "domain", Target.normalized == normalized.normalized)
        ).scalar_one_or_none()
        if t is None or not t.approved:
            raise ValueError("root_domain_requires_admin_approval")

    pipeline = HuntingPipeline(
        root_domain=normalized.normalized,
        status="queued",
        requested_by=requested_by,
        options={"steps": steps, **(options or {})},
        summary={},
    )
    db.add(pipeline)
    db.flush()

    now = dt.datetime.now(dt.timezone.utc)
    for name in (steps or DEFAULT_PIPELINE_STEPS):
        db.add(
            PipelineStep(
                pipeline_id=pipeline.id,
                name=name,
                status="queued",
                progress=0,
                message=None,
                started_at=None,
                finished_at=None,
            )
        )
    db.flush()

    enqueue_hunting_pipeline(str(pipeline.id))
    return pipeline

