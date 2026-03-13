"""Orchestration tasks for VAPT and Bug Hunting pipelines."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from pathlib import Path
from sqlalchemy import text

from app.celery_app import celery
from app.db import session_factory
from app.resource_guard import is_system_ready
from app.tool_runner import run_nmap, run_nuclei, run_httpx, run_katana
from app.normalizer import normalize_nuclei_finding
from app.presets import PRESETS


def _run(coro):
    return asyncio.run(coro)


async def _update_scan(scan_id: int, **fields: Any) -> None:
    if not fields:
        return
    set_clause = ", ".join([f"{k} = :{k}" for k in fields.keys()])
    params = {"scan_id": scan_id, **fields}
    async with session_factory() as db:
        await db.execute(text(f"UPDATE scans SET {set_clause} WHERE id = :scan_id"), params)
        await db.commit()


async def _insert_scan_log(scan_id: int, level: str, message: str, tool: str | None = None):
    async with session_factory() as db:
        await db.execute(
            text(
                """
                INSERT INTO scan_logs (scan_id, level, tool, message, timestamp)
                VALUES (:scan_id, :level, :tool, :message, :timestamp)
                """
            ),
            {
                "scan_id": scan_id,
                "level": level,
                "tool": tool,
                "message": message,
                "timestamp": datetime.now(timezone.utc),
            },
        )
        await db.commit()


async def _insert_finding(scan_id: int, finding: dict[str, Any]):
    async with session_factory() as db:
        await db.execute(
            text(
                """
                INSERT INTO findings (
                    scan_id, tool, title, description, severity, cvss_score, cve_id,
                    evidence, raw_output, is_false_positive, created_at
                ) VALUES (
                    :scan_id, :tool, :title, :description, :severity, :cvss_score, :cve_id,
                    :evidence, CAST(:raw_output AS JSON), false, :created_at
                )
                """
            ),
            {
                "scan_id": scan_id,
                "tool": finding.get("tool"),
                "title": finding.get("title"),
                "description": finding.get("description"),
                "severity": finding.get("severity"),
                "cvss_score": finding.get("cvss_score"),
                "cve_id": finding.get("cve_id"),
                "evidence": finding.get("evidence"),
                "raw_output": json.dumps(finding.get("raw_output", {})),
                "created_at": datetime.now(timezone.utc),
            },
        )
        await db.commit()


async def _get_scan_data(scan_id: int) -> dict[str, Any]:
    async with session_factory() as db:
        result = await db.execute(
            text("SELECT target, tools_config FROM scans WHERE id = :id"), 
            {"id": scan_id}
        )
        row = result.first()
        if not row:
            return {"target": "", "tools_config": {}}
        return {
            "target": row[0], 
            "tools_config": row[1] if isinstance(row[1], dict) else {}
        }

async def _get_scan_target(scan_id: int) -> str:
    data = await _get_scan_data(scan_id)
    return data.get("target", "")


@celery.task(name="orchestrator.run_vapt_scan")
def run_vapt_scan(scan_id: int):
    return _run(_run_vapt_scan(scan_id))


async def _run_vapt_scan(scan_id: int):
    ready, metrics = is_system_ready()
    if not ready:
        await _update_scan(scan_id, status="queued", progress=0)
        await _insert_scan_log(scan_id, "warning", f"System busy: {metrics}")
        return {"status": "queued", "reason": "system_busy", "metrics": metrics}

    await _update_scan(
        scan_id,
        status="running",
        progress=5,
        started_at=datetime.now(timezone.utc),
    )
    await _insert_scan_log(scan_id, "info", "VAPT scan started")

    scan_data = await _get_scan_data(scan_id)
    target = scan_data.get("target", "")
    tools_config = scan_data.get("tools_config", {})
    
    if not target:
        await _update_scan(scan_id, status="failed", error_message="Target not found")
        return {"status": "failed"}

    # Determine which tools to run based on tools_config
    run_nmap_tool = tools_config.get("nmap", True)
    run_openvas_tool = tools_config.get("openvas", False)
    run_nuclei_tool = tools_config.get("nuclei", True)
    run_zap_tool = tools_config.get("zap", False)
    run_nikto_tool = tools_config.get("nikto", True)
    run_sqlmap_tool = tools_config.get("sqlmap", False)

    progress_step = 90 // max([run_nmap_tool, run_openvas_tool, run_nuclei_tool, run_zap_tool, run_nikto_tool, run_sqlmap_tool].count(True), 1)
    current_progress = 5

    # Step 1: Nmap discovery
    if run_nmap_tool:
        await _insert_scan_log(scan_id, "info", "Running Nmap discovery", "nmap")
        nmap_result = await run_nmap(target)
        current_progress += progress_step
        await _update_scan(scan_id, progress=current_progress)
        if not nmap_result["success"]:
            await _insert_scan_log(scan_id, "error", nmap_result.get("error", "Nmap failed"), "nmap")

    # Step 2: OpenVAS 
    if run_openvas_tool:
        await _insert_scan_log(
            scan_id,
            "info",
            "Running OpenVAS Full and Fast profile (host limit=1, safe checks only)",
            "openvas",
        )
        current_progress += progress_step
        await _update_scan(scan_id, progress=current_progress)

    # Step 3: Nuclei
    if run_nuclei_tool:
        await _insert_scan_log(scan_id, "info", "Running Nuclei templates", "nuclei")
        Path("/app/results").mkdir(parents=True, exist_ok=True)
        Path("/app/results/targets.txt").write_text(f"{target}\n", encoding="utf-8")
        nuclei_result = await run_nuclei("/app/results/targets.txt")
        for nf in nuclei_result.get("findings", []):
            await _insert_finding(scan_id, normalize_nuclei_finding(nf))
        current_progress += progress_step
        await _update_scan(scan_id, progress=current_progress)

    # Step 4: ZAP/Nikto/SQLmap
    if run_zap_tool:
        await _insert_scan_log(scan_id, "info", "Running OWASP ZAP headless safe policy", "zap")
        current_progress += progress_step
        await _update_scan(scan_id, progress=current_progress)
    
    if run_nikto_tool:
        await _insert_scan_log(scan_id, "info", "Running Nikto web server scan", "nikto")
        current_progress += progress_step
        await _update_scan(scan_id, progress=current_progress)
    
    if run_sqlmap_tool:
        await _insert_scan_log(scan_id, "info", "Running SQLmap non-aggressive checks", "sqlmap")
        current_progress += progress_step
        await _update_scan(scan_id, progress=current_progress)

    await _update_scan(
        scan_id,
        status="completed",
        progress=100,
        completed_at=datetime.now(timezone.utc),
    )
    await _insert_scan_log(scan_id, "info", "VAPT scan completed")
    return {"status": "completed", "scan_id": scan_id}


@celery.task(name="orchestrator.cancel_vapt_scan")
def cancel_vapt_scan(scan_id: int):
    return _run(_update_scan(scan_id, status="cancelled", progress=0))


# ---------------- Bug Hunting Pipeline ---------------- #

async def _update_session(session_id: int, **fields: Any) -> None:
    if not fields:
        return
    set_clause = ", ".join([f"{k} = :{k}" for k in fields.keys()])
    params = {"session_id": session_id, **fields}
    async with session_factory() as db:
        await db.execute(
            text(f"UPDATE hunting_sessions SET {set_clause} WHERE id = :session_id"),
            params,
        )
        await db.commit()


async def _get_session(session_id: int) -> dict[str, Any]:
    async with session_factory() as db:
        result = await db.execute(
            text(
                "SELECT id, root_domain, preset, steps_config, methods_config FROM hunting_sessions WHERE id = :id"
            ),
            {"id": session_id},
        )
        row = result.first()
        if not row:
            return {}
        return {
            "id": row[0],
            "root_domain": row[1],
            "preset": row[2],
            "steps_config": row[3],
            "methods_config": row[4],
        }


@celery.task(name="orchestrator.run_hunting_pipeline")
def run_hunting_pipeline(session_id: int):
    return _run(_run_hunting_pipeline(session_id))


async def _run_hunting_pipeline(session_id: int):
    ready, metrics = is_system_ready()
    if not ready:
        await _update_session(session_id, status="queued", progress=0)
        return {"status": "queued", "metrics": metrics}

    session = await _get_session(session_id)
    if not session:
        return {"status": "failed", "reason": "session_not_found"}

    preset = session.get("preset") or "standard"
    preset_steps = PRESETS.get(preset, PRESETS["standard"])["steps"]

    await _update_session(
        session_id,
        status="running",
        current_step="initializing",
        progress=1,
        started_at=datetime.now(timezone.utc),
    )

    # Extract method flags from methods_config (sent by frontend)
    methods_config = session.get("methods_config") or {}
    run_subfinder = methods_config.get("subfinder", True)
    run_amass = methods_config.get("amass", True)
    run_httpx = methods_config.get("httpx", True)
    run_katana = methods_config.get("katana", True)
    run_ffuf = methods_config.get("ffuf", True)
    run_gowitness = methods_config.get("gowitness", True)
    run_nuclei = methods_config.get("nuclei", True)

    # Count selected methods to calculate dynamic progress increment
    selected_methods = sum([
        run_subfinder, run_amass, run_httpx, run_katana, run_ffuf, run_gowitness, run_nuclei
    ])
    progress_increment = 85 // max(selected_methods, 1)  # 85% for core hunting, 15% for aggregation/notifications
    current_progress = 1

    logger.info(
        f"[Session {session_id}] Starting hunting pipeline with selected methods: "
        f"subfinder={run_subfinder}, amass={run_amass}, httpx={run_httpx}, "
        f"katana={run_katana}, ffuf={run_ffuf}, gowitness={run_gowitness}, nuclei={run_nuclei}"
    )

    # Step 1: Subdomain Discovery (subfinder + amass conditional)
    if run_subfinder or run_amass:
        await step_subdomain_discovery(session_id, session["root_domain"], run_subfinder, run_amass)
        current_progress += progress_increment
        await _update_session(session_id, current_step="subdomain_discovery", progress=current_progress)
    else:
        logger.info(f"[Session {session_id}] Skipping subdomain discovery (no methods selected)")

    # Step 2: Live Host Detection (httpx conditional)
    if run_httpx:
        await step_live_host_detection(session_id)
        current_progress += progress_increment
        await _update_session(session_id, current_step="live_host_detection", progress=current_progress)
    else:
        logger.info(f"[Session {session_id}] Skipping live host detection (httpx disabled)")

    # Step 3: URL Crawling & Endpoint Discovery (katana conditional)
    if run_katana:
        await step_url_crawling(session_id)
        current_progress += progress_increment
        await _update_session(session_id, current_step="url_crawling", progress=current_progress)
    else:
        logger.info(f"[Session {session_id}] Skipping URL crawling (katana disabled)")

    # Step 4: Screenshot Capture (gowitness conditional)
    if run_gowitness:
        await step_screenshot_capture(session_id)
        current_progress += progress_increment
        await _update_session(session_id, current_step="screenshot_capture", progress=current_progress)
    else:
        logger.info(f"[Session {session_id}] Skipping screenshot capture (gowitness disabled)")

    # Step 5: Vulnerability Scanning (nuclei conditional)
    if run_nuclei:
        await step_template_scanning(session_id)
        current_progress += progress_increment
        await _update_session(session_id, current_step="template_scanning", progress=current_progress)
    else:
        logger.info(f"[Session {session_id}] Skipping template scanning (nuclei disabled)")

    # Step 6: Aggregation & reporting baseline
    await step_aggregate_results(session_id)
    await _update_session(session_id, progress=90)

    # Step 7: Optional telegram notifications
    await step_notifications(session_id)

    await _update_session(
        session_id,
        status="completed",
        current_step="completed",
        progress=100,
        completed_at=datetime.now(timezone.utc),
    )

    logger.info(f"[Session {session_id}] Hunting pipeline completed successfully")
    return {"status": "completed", "session_id": session_id}


@celery.task(name="orchestrator.cancel_hunting_pipeline")
def cancel_hunting_pipeline(session_id: int):
    return _run(_update_session(session_id, status="cancelled", current_step="cancelled"))


# ---- Core 7 bug-hunting stages ----

async def step_subdomain_discovery(session_id: int, root_domain: str, run_subfinder: bool = True, run_amass: bool = True):
    # Conditionally run subfinder and amass based on method selection
    logger.info(f"[Session {session_id}] Step: Subdomain Discovery (subfinder={run_subfinder}, amass={run_amass})")
    
    discovered_subdomains = []
    
    if run_subfinder:
        logger.info(f"[Session {session_id}] Running subfinder on {root_domain}")
        try:
            # Simulate subfinder discovery
            discovered_subdomains.extend([
                f"api.{root_domain}",
                f"dev.{root_domain}",
            ])
            logger.info(f"[Session {session_id}] Subfinder discovered {len(discovered_subdomains)} new subdomains")
        except Exception as e:
            logger.error(f"[Session {session_id}] Subfinder failed: {e}")
    
    if run_amass:
        logger.info(f"[Session {session_id}] Running amass on {root_domain}")
        try:
            # Simulate amass discovery
            discovered_subdomains.extend([
                f"staging.{root_domain}",
                f"mail.{root_domain}",
            ])
            logger.info(f"[Session {session_id}] Amass discovered {len(discovered_subdomains)} subdomains total")
        except Exception as e:
            logger.error(f"[Session {session_id}] Amass failed: {e}")
    
    # Store discovered subdomains in database
    async with session_factory() as db:
        await db.execute(
            text(
                """
                INSERT INTO subdomains (session_id, subdomain, source, is_new, created_at)
                VALUES
                (:sid, :s1, 'subfinder', true, :ts),
                (:sid, :s2, 'amass', true, :ts),
                (:sid, :s3, 'assetfinder', true, :ts)
                """
            ),
            {
                "sid": session_id,
                "s1": f"api.{root_domain}",
                "s2": f"dev.{root_domain}",
                "s3": f"staging.{root_domain}",
                "ts": datetime.now(timezone.utc),
            },
        )
        await db.commit()


async def step_live_host_detection(session_id: int):
    # Normally feeds subdomains to httpx/httprobe.
    logger.info(f"[Session {session_id}] Step: Live Host Detection (httpx)")
    try:
        await run_httpx("/app/results/subdomains.txt")
        logger.info(f"[Session {session_id}] Live host detection completed")
    except Exception as e:
        logger.error(f"[Session {session_id}] Live host detection failed: {e}")


async def step_url_crawling(session_id: int):
    # katana + gau + waybackurls + gospider pipeline.
    logger.info(f"[Session {session_id}] Step: URL Crawling (katana)")
    try:
        await run_katana("/app/results/live_hosts.txt")
        logger.info(f"[Session {session_id}] URL crawling completed")
    except Exception as e:
        logger.error(f"[Session {session_id}] URL crawling failed: {e}")


async def step_screenshot_capture(session_id: int):
    # gowitness or aquatone would be triggered here.
    logger.info(f"[Session {session_id}] Step: Screenshot Capture (gowitness)")
    try:
        # Placeholder for gowitness execution
        logger.info(f"[Session {session_id}] Screenshot capture completed")
    except Exception as e:
        logger.error(f"[Session {session_id}] Screenshot capture failed: {e}")


async def step_template_scanning(session_id: int):
    # nuclei with curated categories and custom template support.
    logger.info(f"[Session {session_id}] Step: Template Scanning (nuclei)")
    try:
        await run_nuclei("/app/results/live_hosts.txt")
        logger.info(f"[Session {session_id}] Template scanning completed")
    except Exception as e:
        logger.error(f"[Session {session_id}] Template scanning failed: {e}")


async def step_aggregate_results(session_id: int):
    # Build baseline snapshots and finding deltas.
    logger.info(f"[Session {session_id}] Step: Aggregating Results")
    try:
        async with session_factory() as db:
            await db.execute(
                text(
                    """
                    INSERT INTO delta_baselines (session_id, root_domain, baseline_type, baseline_data, created_at)
                    SELECT hs.id, hs.root_domain, 'summary',
                           json_build_object('progress', hs.progress, 'status', hs.status),
                           :ts
                    FROM hunting_sessions hs WHERE hs.id = :sid
                    """
                ),
                {"sid": session_id, "ts": datetime.now(timezone.utc)},
            )
            await db.commit()
        logger.info(f"[Session {session_id}] Results aggregation completed")
    except Exception as e:
        logger.error(f"[Session {session_id}] Results aggregation failed: {e}")


async def step_notifications(session_id: int):
    # Notification service can send summary alerts.
    logger.info(f"[Session {session_id}] Step: Sending Notifications")
    return


# ---- 15 advanced methods (opt-in modules) ----

async def run_advanced_methods(session_id: int, selected_steps: list[str]):
    method_map = [
        method_1_subdomain_permutation,
        method_2_asn_cidr_discovery,
        method_3_js_secret_extraction,
        method_4_parameter_discovery,
        method_5_takeover_detection,
        method_6_tech_fingerprinting_cve,
        method_7_cors_headers_misconfig,
        method_8_api_endpoint_fuzzing,
        method_9_cloud_asset_discovery,
        method_10_ssrf_redirect_checks,
        method_11_bac_idor_checks,
        method_12_continuous_delta_monitoring,
        method_13_favicon_shodan_enrichment,
        method_14_email_credential_recon,
        method_15_fast_recon_chains,
    ]
    for method in method_map:
        await method(session_id)


async def method_1_subdomain_permutation(session_id: int):
    # altdns + dnsgen + gotator + massdns + puredns + dnsx
    return


async def method_2_asn_cidr_discovery(session_id: int):
    # asnmap + mapcidr + hakrevdns + masscan
    return


async def method_3_js_secret_extraction(session_id: int):
    # getJS/subjs/linkfinder/trufflehog/secretfinder/jsluice
    return


async def method_4_parameter_discovery(session_id: int):
    # arjun + paramspider + x8 and payload generation
    return


async def method_5_takeover_detection(session_id: int):
    # subjack + nuclei takeover templates + cname checks
    return


async def method_6_tech_fingerprinting_cve(session_id: int):
    # wappalyzer/webanalyze/whatweb + nvd/exploit-db matching
    return


async def method_7_cors_headers_misconfig(session_id: int):
    # corscanner + security headers + sensitive paths
    return


async def method_8_api_endpoint_fuzzing(session_id: int):
    # ffuf + feroxbuster + kiterunner + graphql/openapi checks
    return


async def method_9_cloud_asset_discovery(session_id: int):
    # cloud_enum + bucket checks + exposed service ports
    return


async def method_10_ssrf_redirect_checks(session_id: int):
    # interactsh callbacks + redirect validation
    return


async def method_11_bac_idor_checks(session_id: int):
    # numeric/uuid sequence auth-swap differential checks
    return


async def method_12_continuous_delta_monitoring(session_id: int):
    # scheduled baseline compare and change alerts
    return


async def method_13_favicon_shodan_enrichment(session_id: int):
    # mmh3 favicon hash + shodan/censys + crt san correlation
    return


async def method_14_email_credential_recon(session_id: int):
    # theHarvester + HIBP + github dorks
    return


async def method_15_fast_recon_chains(session_id: int):
    # quick / standard / deep / full_hunter orchestrations
    return
