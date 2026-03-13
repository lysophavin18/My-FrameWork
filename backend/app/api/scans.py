"""VAPT Scan endpoints."""

import re
import ipaddress
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.scan import Scan, Finding
from app.schemas.schemas import ScanCreate, ScanResponse, FindingResponse
from app.core.auth import get_current_user, require_admin
from app.services.scope import classify_target, enforce_scope

router = APIRouter()


def _validate_target(target: str, target_type: str) -> str:
    """Deep validate the scan target format."""
    target = target.strip()
    if target_type == "ip":
        try:
            ipaddress.ip_address(target)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid IP address format")
    elif target_type == "domain":
        pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        if not re.match(pattern, target):
            raise HTTPException(status_code=422, detail="Invalid domain format")
    elif target_type == "url":
        parsed = urlparse(target)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise HTTPException(status_code=422, detail="Invalid URL format (must be http/https)")
    return target


@router.post("/", response_model=ScanResponse, status_code=201)
async def create_scan(
    scan_data: ScanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new VAPT scan for a single target."""
    validated_target = _validate_target(scan_data.target, scan_data.target_type)

    try:
        scope = classify_target(validated_target, scan_data.target_type)
        enforce_scope(scope)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    scan = Scan(
        user_id=current_user.id,
        scan_type="vapt",
        target=scope.normalized,
        target_type=scan_data.target_type,
        tools_config=scan_data.tools_config,
        status="pending_approval" if (scope.is_public and current_user.role != "admin") else "queued",
        approved=(not scope.is_public) or (current_user.role == "admin"),
    )
    db.add(scan)
    await db.flush()
    await db.refresh(scan)

    if scan.approved:
        from app.services.task_dispatcher import dispatch_vapt_scan
        dispatch_vapt_scan(scan.id)

    return scan


@router.post("/{scan_id}/approve", response_model=ScanResponse)
async def approve_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.approved:
        return scan
    if scan.status != "pending_approval":
        raise HTTPException(status_code=409, detail=f"Scan not awaiting approval (status={scan.status})")

    scan.approved = True
    scan.status = "queued"
    await db.flush()

    from app.services.task_dispatcher import dispatch_vapt_scan
    dispatch_vapt_scan(scan.id)
    return scan


@router.post("/{scan_id}/deny", response_model=ScanResponse)
async def deny_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.status in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=409, detail=f"Scan already {scan.status}")

    scan.approved = False
    scan.status = "denied"
    await db.flush()
    return scan


@router.get("/", response_model=list[ScanResponse])
async def list_scans(
    skip: int = 0,
    limit: int = 20,
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Scan).where(Scan.user_id == current_user.id)
    if status:
        query = query.where(Scan.status == status)
    query = query.order_by(desc(Scan.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/{scan_id}/findings", response_model=list[FindingResponse])
async def get_scan_findings(
    scan_id: int,
    severity: str = Query(None),
    tool: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify scan ownership
    scan_result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    if not scan_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Scan not found")

    query = select(Finding).where(Finding.scan_id == scan_id)
    if severity:
        query = query.where(Finding.severity == severity)
    if tool:
        query = query.where(Finding.tool == tool)
    query = query.order_by(Finding.cvss_score.desc().nullslast())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{scan_id}/cancel", response_model=ScanResponse)
async def cancel_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.status in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=409, detail=f"Scan already {scan.status}")

    scan.status = "cancelled"
    await db.flush()

    from app.services.task_dispatcher import cancel_vapt_scan
    cancel_vapt_scan(scan.id)

    return scan
