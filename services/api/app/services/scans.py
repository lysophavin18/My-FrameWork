from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.scan import Scan, ScanStep
from app.db.models.target import Target
from app.services.queue import enqueue_vapt_scan

DEFAULT_STEPS = [
    "validate",
    "nmap",
    "nuclei",
    "nikto",
    "zap",
    "openvas",
    "sqlmap",
    "normalize",
    "report",
]


def create_scan(db: Session, *, target_id: uuid.UUID, requested_by: uuid.UUID) -> Scan:
    target = db.execute(select(Target).where(Target.id == target_id)).scalar_one_or_none()
    if target is None:
        raise ValueError("target_not_found")
    if not target.is_in_allowlist:
        raise ValueError("target_out_of_scope")
    if target.is_public and not target.approved:
        raise ValueError("target_requires_admin_approval")

    scan = Scan(
        target_id=target.id,
        status="queued",
        requested_by=requested_by,
        summary={},
    )
    db.add(scan)
    db.flush()

    now = dt.datetime.now(dt.timezone.utc)
    for name in DEFAULT_STEPS:
        db.add(
            ScanStep(
                scan_id=scan.id,
                name=name,
                status="queued",
                progress=0,
                started_at=None,
                finished_at=None,
                message=None,
            )
        )
    db.flush()

    enqueue_vapt_scan(str(scan.id))
    return scan

