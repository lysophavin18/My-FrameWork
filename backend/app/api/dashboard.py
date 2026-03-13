"""Dashboard endpoints (stats, charts, recent activity)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_db
from app.models.hunting import HuntingSession
from app.models.scan import Finding, Scan
from app.models.user import User
from app.schemas.schemas import DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scan_filter = [] if current_user.role == "admin" else [Scan.user_id == current_user.id]

    total_scans = (
        await db.execute(select(func.count(Scan.id)).where(*scan_filter))
    ).scalar_one()

    active_scans = (
        await db.execute(
            select(func.count(Scan.id)).where(
                *scan_filter,
                Scan.status.in_(["pending", "validating", "queued", "running", "pending_approval"]),
            )
        )
    ).scalar_one()

    total_findings = (
        await db.execute(
            select(func.count(Finding.id)).join(Scan, Finding.scan_id == Scan.id).where(*scan_filter)
        )
    ).scalar_one()

    severity_rows = (
        await db.execute(
            select(Finding.severity, func.count(Finding.id))
            .join(Scan, Finding.scan_id == Scan.id)
            .where(*scan_filter)
            .group_by(Finding.severity)
        )
    ).all()
    severity_counts = {sev: count for sev, count in severity_rows}

    unique_cves = (
        await db.execute(
            select(func.count(distinct(Finding.cve_id)))
            .join(Scan, Finding.scan_id == Scan.id)
            .where(*scan_filter, Finding.cve_id.is_not(None))
        )
    ).scalar_one()

    recent_scans = (
        await db.execute(
            select(Scan.id, Scan.scan_type, Scan.target, Scan.status, Scan.created_at)
            .where(*scan_filter)
            .order_by(desc(Scan.created_at))
            .limit(10)
        )
    ).all()

    hunting_filter = [] if current_user.role == "admin" else [HuntingSession.user_id == current_user.id]
    recent_hunting_sessions = (
        await db.execute(
            select(HuntingSession.id, HuntingSession.root_domain, HuntingSession.status, HuntingSession.created_at)
            .where(*hunting_filter)
            .order_by(desc(HuntingSession.created_at))
            .limit(10)
        )
    ).all()

    return DashboardStats(
        total_scans=total_scans,
        active_scans=active_scans,
        total_findings=total_findings,
        severity_counts=severity_counts,
        unique_cves=unique_cves,
        recent_scans=[
            {
                "id": r.id,
                "scan_type": r.scan_type,
                "target": r.target,
                "status": r.status,
                "created_at": r.created_at,
            }
            for r in recent_scans
        ],
        recent_hunting_sessions=[
            {"id": r.id, "root_domain": r.root_domain, "status": r.status, "created_at": r.created_at}
            for r in recent_hunting_sessions
        ],
    )

