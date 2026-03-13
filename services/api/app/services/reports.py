from __future__ import annotations

import datetime as dt
import json
import os
import uuid

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.finding import Finding
from app.db.models.scan import Scan
from app.db.models.hunting import HuntingPipeline


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def generate_scan_report_files(db: Session, *, scan: Scan) -> dict:
    settings = get_settings()
    reports_dir = settings.reports_dir
    _ensure_dir(reports_dir)

    findings = list(db.execute(select(Finding).where(Finding.scan_id == scan.id)).scalars().all())

    pdf_path = os.path.join(reports_dir, f"scan-{scan.id}.pdf")
    json_path = os.path.join(reports_dir, f"scan-{scan.id}.json")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(48, y, "Expl0V1N - VAPT Report")
    y -= 24
    c.setFont("Helvetica", 10)
    c.drawString(48, y, f"Scan ID: {scan.id}")
    y -= 14
    c.drawString(48, y, f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}")
    y -= 24

    c.setFont("Helvetica-Bold", 12)
    c.drawString(48, y, "Findings")
    y -= 18
    c.setFont("Helvetica", 9)

    for f in findings[:200]:
        line = f"[{f.severity.upper()}] {f.tool}: {f.title}"
        if y < 60:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 9)
        c.drawString(48, y, line[:110])
        y -= 12

    c.save()

    export = {
        "scan_id": str(scan.id),
        "status": scan.status,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "findings": [
            {
                "id": str(f.id),
                "tool": f.tool,
                "title": f.title,
                "severity": f.severity,
                "cvss_score": f.cvss_score,
                "cve_id": f.cve_id,
                "affected_host": f.affected_host,
                "affected_url": f.affected_url,
                "description": f.description,
                "evidence": f.evidence,
                "tags": f.tags,
                "first_seen_at": f.first_seen_at.isoformat(),
                "last_seen_at": f.last_seen_at.isoformat(),
            }
            for f in findings
        ],
    }
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(export, fp, indent=2)

    return {"pdf_path": pdf_path, "json_path": json_path}


def generate_pipeline_report_files(db: Session, *, pipeline: HuntingPipeline) -> dict:
    settings = get_settings()
    reports_dir = settings.reports_dir
    _ensure_dir(reports_dir)

    findings = list(
        db.execute(select(Finding).where(Finding.pipeline_id == pipeline.id)).scalars().all()
    )

    pdf_path = os.path.join(reports_dir, f"pipeline-{pipeline.id}.pdf")
    json_path = os.path.join(reports_dir, f"pipeline-{pipeline.id}.json")

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(48, y, "Expl0V1N - Bug Hunting Report")
    y -= 24
    c.setFont("Helvetica", 10)
    c.drawString(48, y, f"Pipeline ID: {pipeline.id}")
    y -= 14
    c.drawString(48, y, f"Root domain: {pipeline.root_domain}")
    y -= 14
    c.drawString(48, y, f"Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}")
    y -= 24

    c.setFont("Helvetica-Bold", 12)
    c.drawString(48, y, "Findings")
    y -= 18
    c.setFont("Helvetica", 9)

    for f in findings[:200]:
        line = f"[{f.severity.upper()}] {f.tool}: {f.title}"
        if y < 60:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 9)
        c.drawString(48, y, line[:110])
        y -= 12

    c.save()

    export = {
        "pipeline_id": str(pipeline.id),
        "root_domain": pipeline.root_domain,
        "status": pipeline.status,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "findings": [
            {
                "id": str(f.id),
                "tool": f.tool,
                "title": f.title,
                "severity": f.severity,
                "cvss_score": f.cvss_score,
                "cve_id": f.cve_id,
                "affected_host": f.affected_host,
                "affected_url": f.affected_url,
                "description": f.description,
                "evidence": f.evidence,
                "tags": f.tags,
                "first_seen_at": f.first_seen_at.isoformat(),
                "last_seen_at": f.last_seen_at.isoformat(),
            }
            for f in findings
        ],
    }
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(export, fp, indent=2)

    return {"pdf_path": pdf_path, "json_path": json_path}

