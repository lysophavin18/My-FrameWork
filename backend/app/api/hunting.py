"""Bug Hunting endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.hunting import (
    HuntingSession, Subdomain, LiveHost, CrawledURL, Screenshot, HuntingFinding,
)
from app.schemas.schemas import (
    HuntingSessionCreate, HuntingSessionResponse, SubdomainResponse,
    LiveHostResponse, ScreenshotResponse, HuntingFindingResponse,
)
from app.core.auth import get_current_user, require_admin
from app.services.scope import classify_target, enforce_scope

router = APIRouter()


@router.post("/sessions", response_model=HuntingSessionResponse, status_code=201)
async def create_hunting_session(
    data: HuntingSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new bug hunting recon pipeline."""
    try:
        scope = classify_target(data.root_domain, "domain")
        enforce_scope(scope)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    session = HuntingSession(
        user_id=current_user.id,
        root_domain=scope.normalized,
        preset=data.preset,
        steps_config=data.steps_config,
        methods_config=data.methods_config,
        status="pending_approval" if (scope.is_public and current_user.role != "admin") else "queued",
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)

    if session.status == "queued":
        from app.services.task_dispatcher import dispatch_hunting_pipeline
        dispatch_hunting_pipeline(session.id)

    return session


@router.get("/sessions", response_model=list[HuntingSessionResponse])
async def list_sessions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(HuntingSession)
        .where(HuntingSession.user_id == current_user.id)
        .order_by(desc(HuntingSession.created_at))
        .offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/sessions/{session_id}", response_model=HuntingSessionResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(HuntingSession).where(
            HuntingSession.id == session_id,
            HuntingSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/sessions/{session_id}/subdomains", response_model=list[SubdomainResponse])
async def get_subdomains(
    session_id: int,
    source: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session_result = await db.execute(
        select(HuntingSession).where(HuntingSession.id == session_id, HuntingSession.user_id == current_user.id)
    )
    if not session_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    query = select(Subdomain).where(Subdomain.session_id == session_id)
    if source:
        query = query.where(Subdomain.source == source)
    result = await db.execute(query.order_by(Subdomain.subdomain))
    return result.scalars().all()


@router.get("/sessions/{session_id}/live-hosts", response_model=list[LiveHostResponse])
async def get_live_hosts(
    session_id: int,
    alive_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session_result = await db.execute(
        select(HuntingSession).where(HuntingSession.id == session_id, HuntingSession.user_id == current_user.id)
    )
    if not session_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    query = select(LiveHost).where(LiveHost.session_id == session_id)
    if alive_only:
        query = query.where(LiveHost.is_alive == True)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sessions/{session_id}/screenshots", response_model=list[ScreenshotResponse])
async def get_screenshots(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session_result = await db.execute(
        select(HuntingSession).where(HuntingSession.id == session_id, HuntingSession.user_id == current_user.id)
    )
    if not session_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db.execute(
        select(Screenshot).where(Screenshot.session_id == session_id)
    )
    return result.scalars().all()


@router.get("/sessions/{session_id}/findings", response_model=list[HuntingFindingResponse])
async def get_hunting_findings(
    session_id: int,
    severity: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session_result = await db.execute(
        select(HuntingSession).where(HuntingSession.id == session_id, HuntingSession.user_id == current_user.id)
    )
    if not session_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Session not found")

    query = select(HuntingFinding).where(HuntingFinding.session_id == session_id)
    if severity:
        query = query.where(HuntingFinding.severity == severity)
    query = query.order_by(HuntingFinding.cvss_score.desc().nullslast())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/sessions/{session_id}/approve", response_model=HuntingSessionResponse)
async def approve_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(HuntingSession).where(HuntingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "pending_approval":
        return session

    session.status = "queued"
    await db.flush()

    from app.services.task_dispatcher import dispatch_hunting_pipeline
    dispatch_hunting_pipeline(session.id)
    return session


@router.post("/sessions/{session_id}/deny", response_model=HuntingSessionResponse)
async def deny_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    result = await db.execute(select(HuntingSession).where(HuntingSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=409, detail=f"Session already {session.status}")

    session.status = "denied"
    await db.flush()
    return session


@router.post("/sessions/{session_id}/cancel")
async def cancel_hunting(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(HuntingSession).where(
            HuntingSession.id == session_id,
            HuntingSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=409, detail=f"Session already {session.status}")

    session.status = "cancelled"
    await db.flush()

    from app.services.task_dispatcher import cancel_hunting_pipeline
    cancel_hunting_pipeline(session.id)

    return {"status": "cancelled"}
