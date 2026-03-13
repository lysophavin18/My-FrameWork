# Tool Integration Guide

Expl0V1N runs scanners/recon tools as **containerized tool runners** on the `scan-net` network. The **orchestrator** executes tools via `docker exec` (Docker socket mount) and ingests outputs into PostgreSQL.

## Profiles

- `core`: platform + VAPT tool runners
- `hunting`: bug hunting recon tool runners
- `advanced`: opt-in aggressive/large-scope tooling (disabled by default)
- `ai`: AI assistant service

## VAPT tool runners (single target)

| Tool | Service | Purpose | Safety default |
|---|---|---|---|
| Nmap | `nmap` | Port/service discovery (first step) | Conservative timing, limited ports |
| Nuclei | `nuclei` | Template-based checks | Rate limited, severity filtering |
| Nikto | `nikto` | Web server misconfig checks | Disabled unless enabled in scan config |
| OWASP ZAP | `zap` | Web/API scan (headless daemon) | Passive-first (no auto exploitation) |
| OpenVAS/Greenbone | `openvas` | Network vulnerability scan | Max concurrent 1, host limit 1 |
| SQLmap | `sqlmap` | SQLi verification | Controlled mode, off by default |

## Bug hunting runners (root domain pipeline)

| Step | Tools | Output tables |
|---|---|---|
| Subdomains | `subfinder`, `amass`, `assetfinder`, crt.sh (API) | `subdomains` |
| Live hosts | `httpx` | `live_hosts` |
| Crawl/URLs | `katana` (+ optional archive sources) | `crawled_urls` |
| Screenshots | `gowitness` | `screenshots` |
| Findings | `nuclei` | `hunting_findings` |

## Advanced runners (opt-in)

These are disabled unless the `advanced` profile is enabled and the module is explicitly selected:

- DNS scale: `massdns`, `puredns`
- Fast port discovery: `masscan`
- Content discovery: `ffuf`, `feroxbuster`, `kiterunner`
- Parameter discovery: `arjun`
- Secret scanning: `trufflehog`, `linkfinder`
- Takeover checks: `subjack`
- Cloud enumeration: `cloud-enum`
- OOB callbacks: `interactsh`
- Org enrichment: `asnmap`
- Email recon: `theharvester`

## Orchestration and storage

- Orchestrator reads jobs from Redis queues (`vapt`, `hunting`).
- Progress and logs are persisted to PostgreSQL (`scan_logs`, `hunting_sessions.progress`, etc.).
- Artifacts:
  - Scan outputs: `scan-results` volume mounted at `/app/results` (orchestrator)
  - Reports: `reports` volume mounted at `/app/reports` (backend)

## Security notes (important)

- **Scope enforcement** is enforced in the backend (`ALLOW_PUBLIC_TARGETS`, allowlists) and **admin approval** is required for public targets.
- Docker socket access is powerful. For hardening, replace direct socket mounting with a restricted socket proxy and/or run the orchestrator on a dedicated worker node.

