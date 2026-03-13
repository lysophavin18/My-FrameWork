from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import psutil
import redis
from celery import Celery
from sqlalchemy import delete, select, update

from app.config import settings
from app.db import SessionLocal
from app.docker_runner import DockerToolRunner
from app.models import (
    CrawledURL,
    Finding,
    HuntingFinding,
    HuntingSession,
    LiveHost,
    Scan,
    ScanLog,
    Subdomain,
)
from app.parsers import parse_jsonl, parse_nmap_xml
from app.util import ensure_dir, sha256_text, utcnow


celery_app = Celery("expl0v1n_orchestrator", broker=settings.celery_broker_url, backend=settings.celery_result_backend)


def _redis_client() -> redis.Redis:
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _resource_ok() -> tuple[bool, dict[str, Any]]:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    ok = cpu <= settings.scan_cpu_threshold and mem <= settings.scan_ram_threshold
    return ok, {"cpu_percent": cpu, "mem_percent": mem}


def _log_scan(db, scan_id: int, message: str, level: str = "info", tool: str | None = None) -> None:
    db.add(
        ScanLog(
            scan_id=scan_id,
            level=level,
            tool=tool,
            message=message,
            timestamp=utcnow(),
        )
    )


def _publish(channel: str, payload: dict) -> None:
    try:
        _redis_client().publish(channel, payload)
    except Exception:
        pass


@celery_app.task(name="orchestrator.run_vapt_scan", bind=True, acks_late=True)
def run_vapt_scan(self, scan_id: int):
    ok, metrics = _resource_ok()
    if not ok:
        raise self.retry(countdown=60, max_retries=30)

    runner = DockerToolRunner()
    ensure_dir(settings.results_dir)

    db = SessionLocal()
    try:
        scan = db.execute(select(Scan).where(Scan.id == scan_id)).scalar_one_or_none()
        if scan is None:
            return
        if not scan.approved:
            _log_scan(db, scan_id, "Scan not approved; skipping execution", level="warning")
            db.commit()
            return
        if scan.status in {"cancelled", "canceled", "denied"}:
            return

        scan.status = "running"
        scan.started_at = utcnow()
        scan.progress = 1
        _log_scan(db, scan_id, f"Starting VAPT scan on target={scan.target}", tool=None)
        db.commit()

        host = scan.target
        if scan.target_type == "url":
            host = urlparse(scan.target).hostname or scan.target

        # Step 1: Nmap discovery
        _log_scan(db, scan_id, "Running Nmap discovery", tool="nmap")
        db.commit()
        nmap_res = runner.exec(
            container_name="expl0v1n-nmap",
            cmd=["nmap", "-sV", "-T3", "--top-ports", "1000", "--max-retries", "2", "-oX", "-", host],
        )
        if nmap_res.exit_code != 0:
            _log_scan(db, scan_id, f"Nmap failed: {nmap_res.stderr[:4000]}", level="error", tool="nmap")
            scan.status = "failed"
            scan.error_message = "nmap_failed"
            db.commit()
            return

        nmap_path = os.path.join(settings.results_dir, f"scan_{scan_id}_nmap.xml")
        with open(nmap_path, "w", encoding="utf-8") as fp:
            fp.write(nmap_res.stdout)

        nmap_parsed = parse_nmap_xml(nmap_res.stdout)
        open_ports = nmap_parsed.get("open_ports", [])
        _log_scan(db, scan_id, f"Nmap open ports: {len(open_ports)}", tool="nmap")

        web_urls: list[str] = []
        if scan.target_type == "url":
            web_urls = [scan.target]
        else:
            ports = {p["port"] for p in open_ports if p.get("proto") == "tcp"}
            if 80 in ports:
                web_urls.append(f"http://{host}")
            if 443 in ports:
                web_urls.append(f"https://{host}")
            for p in sorted(ports.intersection({8080, 8000, 3000})):
                web_urls.append(f"http://{host}:{p}")
            for p in sorted(ports.intersection({8443})):
                web_urls.append(f"https://{host}:{p}")
            if not web_urls and scan.target_type in {"ip", "domain"}:
                web_urls = [f"http://{host}", f"https://{host}"]

        scan.progress = 25
        db.commit()

        # Step 2: Nuclei (template scan) on discovered web URLs
        if web_urls:
            _log_scan(db, scan_id, f"Running nuclei against {len(web_urls)} URL(s)", tool="nuclei")
            db.commit()
            findings_added = 0
            for url in web_urls[:20]:
                nuclei_res = runner.exec(
                    container_name="expl0v1n-nuclei",
                    cmd=[
                        "nuclei",
                        "-u",
                        url,
                        "-jsonl",
                        "-severity",
                        "critical,high,medium,low,info",
                        "-rl",
                        "150",
                    ],
                )
                for item in parse_jsonl(nuclei_res.stdout):
                    info = item.get("info") or {}
                    title = info.get("name") or item.get("template-id") or "nuclei finding"
                    severity = (info.get("severity") or "info").lower()
                    cve_id = None
                    classification = info.get("classification") or {}
                    cve_list = classification.get("cve-id") or classification.get("cve") or []
                    if isinstance(cve_list, list) and cve_list:
                        cve_id = cve_list[0]
                    dedup = sha256_text(f"nuclei|{title}|{url}|{cve_id or ''}")
                    db.add(
                        Finding(
                            scan_id=scan_id,
                            tool="nuclei",
                            title=title,
                            description=info.get("description"),
                            severity=severity,
                            cvss_score=None,
                            cve_id=cve_id,
                            cwe_id=None,
                            affected_component=url,
                            evidence=item.get("matched-at") or url,
                            remediation=None,
                            raw_output=item,
                            is_false_positive=False,
                            created_at=utcnow(),
                        )
                    )
                    findings_added += 1
            _log_scan(db, scan_id, f"Nuclei findings added: {findings_added}", tool="nuclei")
            scan.progress = 60
            db.commit()

        # TODO: OpenVAS, ZAP, Nikto, SQLmap integrations (safe defaults only).
        _log_scan(db, scan_id, "Completing scan (placeholders for remaining tools)", tool=None)
        scan.status = "completed"
        scan.progress = 100
        scan.completed_at = utcnow()
        db.commit()
    except Exception as exc:
        db.rollback()
        db2 = SessionLocal()
        try:
            scan = db2.execute(select(Scan).where(Scan.id == scan_id)).scalar_one_or_none()
            if scan is not None:
                scan.status = "failed"
                scan.error_message = str(exc)
                db2.add(
                    ScanLog(
                        scan_id=scan_id,
                        level="error",
                        tool=None,
                        message=f"Unhandled orchestrator error: {exc}",
                        timestamp=utcnow(),
                    )
                )
                db2.commit()
        finally:
            db2.close()
        raise
    finally:
        db.close()


@celery_app.task(name="orchestrator.cancel_vapt_scan")
def cancel_vapt_scan(scan_id: int):
    db = SessionLocal()
    try:
        scan = db.execute(select(Scan).where(Scan.id == scan_id)).scalar_one_or_none()
        if scan is None:
            return
        scan.status = "cancelled"
        scan.completed_at = utcnow()
        scan.progress = 100
        _log_scan(db, scan_id, "Scan cancelled by user", level="warning")
        db.commit()
    finally:
        db.close()


@celery_app.task(name="orchestrator.run_hunting_pipeline", bind=True, acks_late=True)
def run_hunting_pipeline(self, session_id: int):
    ok, _ = _resource_ok()
    if not ok:
        raise self.retry(countdown=60, max_retries=30)

    runner = DockerToolRunner()
    db = SessionLocal()
    try:
        session = db.execute(select(HuntingSession).where(HuntingSession.id == session_id)).scalar_one_or_none()
        if session is None:
            return
        if session.status in {"cancelled", "canceled", "denied"}:
            return

        session.status = "running"
        session.started_at = utcnow()
        session.progress = 1
        session.current_step = "subdomains"
        db.commit()

        root_domain = session.root_domain

        # Step 1: subdomain discovery (subfinder + amass)
        subdomains: set[str] = set()
        subfinder_res = runner.exec(
            container_name="expl0v1n-subfinder",
            cmd=["subfinder", "-d", root_domain, "-silent"],
        )
        for line in subfinder_res.stdout.splitlines():
            line = line.strip()
            if line:
                subdomains.add(line)

        amass_res = runner.exec(
            container_name="expl0v1n-amass",
            cmd=["amass", "enum", "-passive", "-d", root_domain],
        )
        for line in amass_res.stdout.splitlines():
            line = line.strip()
            if line and line.endswith(root_domain):
                subdomains.add(line)

        assetfinder_res = runner.exec(
            container_name="expl0v1n-assetfinder",
            cmd=["assetfinder", "--subs-only", root_domain],
        )
        for line in assetfinder_res.stdout.splitlines():
            line = line.strip()
            if line and line.endswith(root_domain):
                subdomains.add(line)

        # Persist
        db.execute(delete(Subdomain).where(Subdomain.session_id == session_id))
        for sd in sorted(subdomains):
            db.add(Subdomain(session_id=session_id, subdomain=sd, source="passive", is_new=True, created_at=utcnow()))
        session.progress = 25
        session.current_step = "live_hosts"
        db.commit()

        # Step 2: live host detection (httpx)
        live_hosts: list[dict] = []
        if subdomains:
            targets_text = "\n".join(sorted(subdomains))
            runner.put_text(container_name="expl0v1n-httpx", path="/tmp/targets.txt", content=targets_text)
            httpx_res = runner.exec(
                container_name="expl0v1n-httpx",
                cmd=[
                    "httpx",
                    "-silent",
                    "-json",
                    "-l",
                    "/tmp/targets.txt",
                    "-ports",
                    "80,443,8080,8443,8000,3000",
                    "-timeout",
                    "10",
                ],
            )
            live_hosts = parse_jsonl(httpx_res.stdout)

        db.execute(delete(LiveHost).where(LiveHost.session_id == session_id))
        for item in live_hosts:
            url = item.get("url") or item.get("input") or ""
            if not url:
                continue
            db.add(
                LiveHost(
                    session_id=session_id,
                    url=url,
                    status_code=item.get("status_code"),
                    title=item.get("title"),
                    technologies=item.get("tech") or item.get("technologies"),
                    content_length=item.get("content_length"),
                    is_alive=True,
                    port=item.get("port"),
                    created_at=utcnow(),
                )
            )
        session.progress = 50
        session.current_step = "crawl"
        db.commit()

        # Step 3: URL crawling (katana)
        urls: set[str] = set()
        # In this scaffold we avoid aggressive crawling; use katana with conservative defaults.
        # TODO: Implement piping host list to katana via mounted file.
        for lh in db.execute(select(LiveHost).where(LiveHost.session_id == session_id)).scalars().all():
            if not lh.url:
                continue
            katana_res = runner.exec(
                container_name="expl0v1n-katana",
                cmd=["katana", "-u", lh.url, "-silent"],
            )
            for line in katana_res.stdout.splitlines():
                line = line.strip()
                if line.startswith("http"):
                    urls.add(line)

        db.execute(delete(CrawledURL).where(CrawledURL.session_id == session_id))
        for u in sorted(list(urls))[:5000]:
            db.add(CrawledURL(session_id=session_id, url=u, source="katana", category=None, parameters=None, created_at=utcnow()))
        session.progress = 75
        session.current_step = "nuclei"
        db.commit()

        # Step 4/5: nuclei template scan against live hosts (shared)
        findings_added = 0
        for lh in db.execute(select(LiveHost).where(LiveHost.session_id == session_id)).scalars().all():
            if not lh.url:
                continue
            nuclei_res = runner.exec(
                container_name="expl0v1n-nuclei",
                cmd=[
                    "nuclei",
                    "-u",
                    lh.url,
                    "-jsonl",
                    "-severity",
                    "critical,high,medium,low,info",
                    "-rl",
                    "150",
                ],
            )
            for item in parse_jsonl(nuclei_res.stdout):
                info = item.get("info") or {}
                title = info.get("name") or item.get("template-id") or "nuclei finding"
                severity = (info.get("severity") or "info").lower()
                db.add(
                    HuntingFinding(
                        session_id=session_id,
                        tool="nuclei",
                        template_id=item.get("template-id"),
                        title=title,
                        severity=severity,
                        url=item.get("matched-at") or lh.url,
                        is_new=True,
                        cve_id=None,
                        cvss_score=None,
                        raw_output=item,
                        created_at=utcnow(),
                    )
                )
                findings_added += 1
        session.progress = 100
        session.current_step = "completed"
        session.status = "completed"
        session.completed_at = utcnow()
        db.commit()
    except Exception as exc:
        db.rollback()
        db2 = SessionLocal()
        try:
            session = db2.execute(select(HuntingSession).where(HuntingSession.id == session_id)).scalar_one_or_none()
            if session is not None:
                session.status = "failed"
                session.error_message = str(exc)
                session.completed_at = utcnow()
                db2.commit()
        finally:
            db2.close()
        raise
    finally:
        db.close()


@celery_app.task(name="orchestrator.cancel_hunting_pipeline")
def cancel_hunting_pipeline(session_id: int):
    db = SessionLocal()
    try:
        session = db.execute(select(HuntingSession).where(HuntingSession.id == session_id)).scalar_one_or_none()
        if session is None:
            return
        session.status = "cancelled"
        session.completed_at = utcnow()
        session.progress = 100
        db.commit()
    finally:
        db.close()
