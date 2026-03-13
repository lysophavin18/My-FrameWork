"""Report generation endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.models.hunting import HuntingSession
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/vapt/{scan_id}/pdf")
async def download_vapt_report(
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
    if scan.status != "completed":
        raise HTTPException(status_code=409, detail="Scan not yet completed")

    from app.services.report_generator import generate_vapt_pdf
    pdf_path = await generate_vapt_pdf(scan_id)

    return FileResponse(
        path=pdf_path,
        filename=f"vapt_report_{scan_id}.pdf",
        media_type="application/pdf",
    )


@router.get("/vapt/{scan_id}/json")
async def download_vapt_json(
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

    from app.services.report_generator import generate_vapt_json
    json_path = await generate_vapt_json(scan_id)

    return FileResponse(
        path=json_path,
        filename=f"vapt_report_{scan_id}.json",
        media_type="application/json",
    )


@router.get("/hunting/{session_id}/pdf")
async def download_hunting_report(
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

    from app.services.report_generator import generate_hunting_pdf
    pdf_path = await generate_hunting_pdf(session_id)

    return FileResponse(
        path=pdf_path,
        filename=f"hunting_report_{session_id}.pdf",
        media_type="application/pdf",
    )


@router.get("/hunting/{session_id}/json")
async def download_hunting_json(
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

    from app.services.report_generator import generate_hunting_json
    json_path = await generate_hunting_json(session_id)

    return FileResponse(
        path=json_path,
        filename=f"hunting_report_{session_id}.json",
        media_type="application/json",
    )
