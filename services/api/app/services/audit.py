from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.db.models.audit import AuditLog


def write_audit_log(
    *,
    db: Session,
    request_id: str,
    user_id: str | None,
    method: str,
    path: str,
    status_code: int,
    ip: str | None,
    user_agent: str | None,
    duration_ms: int,
    metadata: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            request_id=request_id,
            user_id=uuid.UUID(user_id) if user_id else None,
            method=method,
            path=path,
            status_code=status_code,
            ip=ip,
            user_agent=user_agent,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )
    )

