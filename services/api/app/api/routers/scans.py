from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from app.api.deps import get_current_user
from app.db.models.finding import Finding
from app.db.models.scan import Scan, ScanStep
from app.db.session import get_db
from app.schemas.finding import FindingOut
from app.schemas.scan import ScanCreateRequest, ScanDetailOut, ScanOut, ScanStepOut
from app.services.reports import generate_scan_report_files
from app.services.scans import create_scan

router = APIRouter()


@router.post("", response_model=ScanOut)
def create(payload: ScanCreateRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    scan = create_scan(db=db, target_id=payload.target_id, requested_by=user.id)
    db.commit()
    return ScanOut(
        id=scan.id,
        target_id=scan.target_id,
        status=scan.status,
        requested_by=scan.requested_by,
        started_at=scan.started_at,
        finished_at=scan.finished_at,
        summary=scan.summary,
        created_at=scan.created_at,
    )


@router.get("", response_model=list[ScanOut])
def list_scans(db: Session = Depends(get_db), user=Depends(get_current_user)):
    stmt = select(Scan).order_by(Scan.created_at.desc())
    if user.role != "admin":
        stmt = stmt.where(Scan.requested_by == user.id)
    scans = list(db.execute(stmt).scalars().all())
    return [
        ScanOut(
            id=s.id,
            target_id=s.target_id,
            status=s.status,
            requested_by=s.requested_by,
            started_at=s.started_at,
            finished_at=s.finished_at,
            summary=s.summary,
            created_at=s.created_at,
        )
        for s in scans
    ]


@router.get("/{scan_id}", response_model=ScanDetailOut)
def get_scan(scan_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    scan = db.execute(select(Scan).where(Scan.id == scan_id)).scalar_one_or_none()
    if scan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    if user.role != "admin" and scan.requested_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    steps = list(db.execute(select(ScanStep).where(ScanStep.scan_id == scan.id)).scalars().all())
    return ScanDetailOut(
        id=scan.id,
        target_id=scan.target_id,
        status=scan.status,
        requested_by=scan.requested_by,
        started_at=scan.started_at,
        finished_at=scan.finished_at,
        summary=scan.summary,
        created_at=scan.created_at,
        steps=[
            ScanStepOut(
                id=st.id,
                name=st.name,
                status=st.status,
                progress=st.progress,
                message=st.message,
                started_at=st.started_at,
                finished_at=st.finished_at,
            )
            for st in steps
        ],
    )


@router.post("/{scan_id}/cancel")
def cancel(scan_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    scan = db.execute(select(Scan).where(Scan.id == scan_id)).scalar_one_or_none()
    if scan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    if user.role != "admin" and scan.requested_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    if scan.status in {"completed", "failed", "canceled"}:
        return {"status": scan.status}

    scan.status = "canceled"
    db.commit()
    return {"status": "canceled"}


@router.get("/{scan_id}/findings", response_model=list[FindingOut])
def list_findings(scan_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    scan = db.execute(select(Scan).where(Scan.id == scan_id)).scalar_one_or_none()
    if scan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    if user.role != "admin" and scan.requested_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    findings = list(db.execute(select(Finding).where(Finding.scan_id == scan_id)).scalars().all())
    return [
        FindingOut(
            id=f.id,
            tool=f.tool,
            title=f.title,
            severity=f.severity,
            cvss_score=f.cvss_score,
            cve_id=f.cve_id,
            affected_host=f.affected_host,
            affected_url=f.affected_url,
            description=f.description,
            evidence=f.evidence,
            tags=f.tags,
            first_seen_at=f.first_seen_at,
            last_seen_at=f.last_seen_at,
        )
        for f in findings
    ]


@router.get("/{scan_id}/report.pdf")
def report_pdf(scan_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    scan = db.execute(select(Scan).where(Scan.id == scan_id)).scalar_one_or_none()
    if scan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    if user.role != "admin" and scan.requested_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    pdf_path = (scan.summary or {}).get("report_pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        paths = generate_scan_report_files(db=db, scan=scan)
        scan.summary = {**(scan.summary or {}), "report_pdf_path": paths["pdf_path"], "report_json_path": paths["json_path"]}
        db.commit()
        pdf_path = paths["pdf_path"]

    return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))


@router.get("/{scan_id}/report.json")
def report_json(scan_id: uuid.UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    scan = db.execute(select(Scan).where(Scan.id == scan_id)).scalar_one_or_none()
    if scan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")
    if user.role != "admin" and scan.requested_by != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")

    json_path = (scan.summary or {}).get("report_json_path")
    if not json_path or not os.path.exists(json_path):
        paths = generate_scan_report_files(db=db, scan=scan)
        scan.summary = {**(scan.summary or {}), "report_pdf_path": paths["pdf_path"], "report_json_path": paths["json_path"]}
        db.commit()
        json_path = paths["json_path"]

    return FileResponse(json_path, media_type="application/json", filename=os.path.basename(json_path))

