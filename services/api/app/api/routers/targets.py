from __future__ import annotations

import datetime as dt
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.models.target import Target
from app.db.session import get_db
from app.schemas.target import TargetApproveRequest, TargetCreateRequest, TargetOut
from app.services.targets import enforce_scope, normalize_target

router = APIRouter()


@router.post("", response_model=TargetOut)
def create_target(
    payload: TargetCreateRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    normalized = normalize_target(payload.input)
    enforce_scope(normalized)

    auto_approve = (not normalized.is_public) and normalized.is_in_allowlist
    target = Target(
        type=normalized.type,
        input=normalized.input,
        normalized=normalized.normalized,
        root_domain=normalized.root_domain,
        is_public=normalized.is_public,
        is_in_allowlist=normalized.is_in_allowlist,
        created_by=user.id,
        approved=auto_approve,
        approved_by=user.id if auto_approve else None,
        approved_at=dt.datetime.now(dt.timezone.utc) if auto_approve else None,
        approval_note="auto-approved (internal scope)" if auto_approve else None,
    )
    db.add(target)
    db.commit()

    return TargetOut(
        id=target.id,
        type=target.type,
        input=target.input,
        normalized=target.normalized,
        root_domain=target.root_domain,
        is_public=target.is_public,
        is_in_allowlist=target.is_in_allowlist,
        approved=target.approved,
        approved_by=target.approved_by,
        approved_at=target.approved_at,
        approval_note=target.approval_note,
        created_by=target.created_by,
        created_at=target.created_at,
    )


@router.get("", response_model=list[TargetOut])
def list_targets(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    stmt = select(Target).order_by(Target.created_at.desc())
    if user.role != "admin":
        stmt = stmt.where(Target.created_by == user.id)

    targets = list(db.execute(stmt).scalars().all())
    return [
        TargetOut(
            id=t.id,
            type=t.type,
            input=t.input,
            normalized=t.normalized,
            root_domain=t.root_domain,
            is_public=t.is_public,
            is_in_allowlist=t.is_in_allowlist,
            approved=t.approved,
            approved_by=t.approved_by,
            approved_at=t.approved_at,
            approval_note=t.approval_note,
            created_by=t.created_by,
            created_at=t.created_at,
        )
        for t in targets
    ]


@router.post("/{target_id}/approve", response_model=TargetOut, dependencies=[Depends(require_admin)])
def approve_target(target_id: uuid.UUID, payload: TargetApproveRequest, db: Session = Depends(get_db), admin=Depends(require_admin)):
    target = db.execute(select(Target).where(Target.id == target_id)).scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")

    target.approved = True
    target.approved_by = admin.id
    target.approved_at = dt.datetime.now(dt.timezone.utc)
    target.approval_note = payload.note
    db.commit()
    return TargetOut(
        id=target.id,
        type=target.type,
        input=target.input,
        normalized=target.normalized,
        root_domain=target.root_domain,
        is_public=target.is_public,
        is_in_allowlist=target.is_in_allowlist,
        approved=target.approved,
        approved_by=target.approved_by,
        approved_at=target.approved_at,
        approval_note=target.approval_note,
        created_by=target.created_by,
        created_at=target.created_at,
    )


@router.post("/{target_id}/deny", response_model=TargetOut, dependencies=[Depends(require_admin)])
def deny_target(target_id: uuid.UUID, payload: TargetApproveRequest, db: Session = Depends(get_db), admin=Depends(require_admin)):
    target = db.execute(select(Target).where(Target.id == target_id)).scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")

    target.approved = False
    target.approved_by = admin.id
    target.approved_at = dt.datetime.now(dt.timezone.utc)
    target.approval_note = payload.note
    db.commit()
    return TargetOut(
        id=target.id,
        type=target.type,
        input=target.input,
        normalized=target.normalized,
        root_domain=target.root_domain,
        is_public=target.is_public,
        is_in_allowlist=target.is_in_allowlist,
        approved=target.approved,
        approved_by=target.approved_by,
        approved_at=target.approved_at,
        approval_note=target.approval_note,
        created_by=target.created_by,
        created_at=target.created_at,
    )

