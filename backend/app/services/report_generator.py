"""PDF/JSON report generation utilities."""

import json
from pathlib import Path
from sqlalchemy import select
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.database import async_session
from app.models.scan import Scan, Finding
from app.models.hunting import (
    HuntingSession, Subdomain, LiveHost, CrawledURL, Screenshot, HuntingFinding,
)

REPORT_DIR = Path("/app/reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
_jinja = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


async def generate_vapt_json(scan_id: int) -> str:
    async with async_session() as db:
        scan_result = await db.execute(select(Scan).where(Scan.id == scan_id))
        scan = scan_result.scalar_one()

        findings_result = await db.execute(select(Finding).where(Finding.scan_id == scan_id))
        findings = findings_result.scalars().all()

        payload = {
            "scan": {
                "id": scan.id,
                "target": scan.target,
                "status": scan.status,
                "created_at": scan.created_at.isoformat() if scan.created_at else None,
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
            },
            "findings": [
                {
                    "tool": f.tool,
                    "title": f.title,
                    "severity": f.severity,
                    "cvss_score": f.cvss_score,
                    "cve_id": f.cve_id,
                    "description": f.description,
                    "evidence": f.evidence,
                    "remediation": f.remediation,
                }
                for f in findings
            ],
        }

        output = REPORT_DIR / f"vapt_report_{scan_id}.json"
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(output)


async def generate_hunting_json(session_id: int) -> str:
    async with async_session() as db:
        session_result = await db.execute(select(HuntingSession).where(HuntingSession.id == session_id))
        hs = session_result.scalar_one()

        subdomains = (await db.execute(select(Subdomain).where(Subdomain.session_id == session_id))).scalars().all()
        live_hosts = (await db.execute(select(LiveHost).where(LiveHost.session_id == session_id))).scalars().all()
        urls = (await db.execute(select(CrawledURL).where(CrawledURL.session_id == session_id))).scalars().all()
        screenshots = (await db.execute(select(Screenshot).where(Screenshot.session_id == session_id))).scalars().all()
        findings = (await db.execute(select(HuntingFinding).where(HuntingFinding.session_id == session_id))).scalars().all()

        payload = {
            "session": {
                "id": hs.id,
                "root_domain": hs.root_domain,
                "status": hs.status,
                "preset": hs.preset,
                "started_at": hs.started_at.isoformat() if hs.started_at else None,
                "completed_at": hs.completed_at.isoformat() if hs.completed_at else None,
            },
            "summary": {
                "total_subdomains": len(subdomains),
                "total_live_hosts": len([h for h in live_hosts if h.is_alive]),
                "total_urls": len(urls),
                "total_findings": len(findings),
            },
            "subdomains": [s.subdomain for s in subdomains],
            "live_hosts": [h.url for h in live_hosts if h.is_alive],
            "urls": [u.url for u in urls],
            "screenshots": [s.file_path for s in screenshots],
            "findings": [
                {
                    "tool": f.tool,
                    "title": f.title,
                    "severity": f.severity,
                    "url": f.url,
                    "template_id": f.template_id,
                }
                for f in findings
            ],
        }

        output = REPORT_DIR / f"hunting_report_{session_id}.json"
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(output)


async def generate_vapt_pdf(scan_id: int) -> str:
    async with async_session() as db:
        scan = (await db.execute(select(Scan).where(Scan.id == scan_id))).scalar_one()
        findings = (await db.execute(select(Finding).where(Finding.scan_id == scan_id))).scalars().all()

    template = _jinja.get_template("vapt_report.html")
    html = template.render(scan=scan, findings=findings)

    pdf_path = REPORT_DIR / f"vapt_report_{scan_id}.pdf"
    HTML(string=html, base_url=str(TEMPLATE_DIR)).write_pdf(str(pdf_path))
    return str(pdf_path)


async def generate_hunting_pdf(session_id: int) -> str:
    async with async_session() as db:
        hs = (await db.execute(select(HuntingSession).where(HuntingSession.id == session_id))).scalar_one()
        subdomains = (await db.execute(select(Subdomain).where(Subdomain.session_id == session_id))).scalars().all()
        live_hosts = (await db.execute(select(LiveHost).where(LiveHost.session_id == session_id))).scalars().all()
        urls = (await db.execute(select(CrawledURL).where(CrawledURL.session_id == session_id))).scalars().all()
        screenshots = (await db.execute(select(Screenshot).where(Screenshot.session_id == session_id))).scalars().all()
        findings = (await db.execute(select(HuntingFinding).where(HuntingFinding.session_id == session_id))).scalars().all()

    template = _jinja.get_template("hunting_report.html")
    html = template.render(
        session=hs,
        subdomains=subdomains,
        live_hosts=live_hosts,
        urls=urls,
        screenshots=screenshots,
        findings=findings,
    )

    pdf_path = REPORT_DIR / f"hunting_report_{session_id}.pdf"
    HTML(string=html, base_url=str(TEMPLATE_DIR)).write_pdf(str(pdf_path))
    return str(pdf_path)
