from __future__ import annotations

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Finding, HuntingFinding, HuntingSession, Scan


def build_context(*, scan_id: int | None, session_id: int | None) -> str:
    db = SessionLocal()
    try:
        parts: list[str] = []
        if scan_id is not None:
            scan = db.execute(select(Scan).where(Scan.id == scan_id)).scalar_one_or_none()
            if scan:
                parts.append(f"Scan {scan.id} target={scan.target} status={scan.status}")
                findings = list(
                    db.execute(select(Finding).where(Finding.scan_id == scan_id).limit(30)).scalars().all()
                )
                for f in findings:
                    parts.append(f"- [{f.severity}] {f.tool}: {f.title} (CVE={f.cve_id or 'n/a'})")
        if session_id is not None:
            hs = db.execute(select(HuntingSession).where(HuntingSession.id == session_id)).scalar_one_or_none()
            if hs:
                parts.append(f"Hunting session {hs.id} root_domain={hs.root_domain} status={hs.status}")
                findings = list(
                    db.execute(select(HuntingFinding).where(HuntingFinding.session_id == session_id).limit(30)).scalars().all()
                )
                for f in findings:
                    parts.append(f"- [{f.severity}] {f.tool}: {f.title} url={f.url or 'n/a'}")
        return "\n".join(parts).strip()
    finally:
        db.close()

