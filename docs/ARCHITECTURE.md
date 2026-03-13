# Expl0V1N Architecture

## 1) System Architecture (VAPT + Bug Hunting + Advanced + AI)

```mermaid
flowchart LR
  U[Security Engineer] --> FE[Frontend React UI]
  FE --> NGINX[Nginx API Gateway]
  NGINX --> API[Backend API FastAPI]
  API --> PG[(PostgreSQL)]
  API --> REDIS[(Redis Queue)]
  API --> ORCH[Scan Orchestrator Celery]
  ORCH --> REDIS
  ORCH --> PG

  ORCH --> NMAP[Nmap]
  ORCH --> OPENVAS[OpenVAS]
  ORCH --> NUCLEI[Nuclei]
  ORCH --> ZAP[OWASP ZAP]
  ORCH --> NIKTO[Nikto]
  ORCH --> SQLMAP[SQLmap]

  ORCH --> BH[Bug Hunting Toolchain]
  BH --> SUBD[Subfinder/Amass/Assetfinder/crt.sh]
  BH --> LIVE[httpx]
  BH --> CRAWL[Katana/gau/wayback/gospider]
  BH --> SHOT[Gowitness]
  BH --> ADV[Advanced Methods 1-15]

  API --> NOTIF[Notification Service]
  API --> AI[AI Assistant Service]
  AI --> LLM[OpenAI/Ollama-Compatible Endpoint]
```

## 2) Service Responsibility Breakdown (35 Services)

| # | Service | Responsibility |
|---|---|---|
| 1 | frontend | Web UI, auth UX, dashboard, scan forms, AI chat widget |
| 2 | backend | REST API, RBAC, validation, audit logging, report APIs |
| 3 | orchestrator | Queue workers, execution sequencing, normalization |
| 4 | redis | Celery broker/result backend, event bus |
| 5 | postgres | Persistent state for all scans/findings/history |
| 6 | openvas | Safe network vuln scanning with strict host/concurrency limits |
| 7 | nmap | Port/service discovery and seed data for other tools |
| 8 | nuclei | Template-based scanning (VAPT + Hunting) |
| 9 | zap | Headless web/API scanner |
| 10 | nikto | Web server misconfiguration discovery |
| 11 | sqlmap | Controlled SQL injection checks |
| 12 | metasploit | CVE/exploit matching only, no auto exploit |
| 13 | subfinder | Passive subdomain enumeration |
| 14 | amass | Passive ASN/subdomain intel enrichment |
| 15 | httpx | Live host probing + metadata |
| 16 | katana | URL/endpoint crawling |
| 17 | nuclei (shared) | Bug hunting template execution |
| 18 | gowitness | Screenshot capture and gallery artifacts |
| 19 | notification-service | Telegram alerts (extensible to webhooks) |
| 20 | ai-assistant | Context-aware LLM proxy, policy and rate limit |
| 21 | massdns | High-throughput DNS resolution |
| 22 | puredns | Wildcard filtering + resolver validation |
| 23 | altdns-dnsgen | Subdomain permutations/mutations |
| 24 | masscan | High-speed SYN scan for CIDR inventory |
| 25 | ffuf | Fast web/API content fuzzing |
| 26 | feroxbuster | Recursive content discovery |
| 27 | kiterunner | API route brute force/discovery |
| 28 | arjun | Hidden parameter discovery |
| 29 | trufflehog | Secret scanning in JS/content artifacts |
| 30 | linkfinder/jsluice | JS endpoint and token extraction |
| 31 | subjack | Subdomain takeover checks |
| 32 | cloud-enum | Cloud asset exposure discovery |
| 33 | interactsh | OOB callback infrastructure for SSRF validation |
| 34 | theharvester | Email/account reconnaissance |
| 35 | asnmap+mapcidr | ASN->CIDR expansion and infra correlation |

## 3) VAPT Data Flow

```mermaid
sequenceDiagram
  participant UI as Frontend
  participant API as Backend
  participant Q as Redis/Celery
  participant ORCH as Orchestrator
  participant DB as PostgreSQL

  UI->>API: POST /scans (single target)
  API->>API: Validate format + auth + approval gate
  API->>Q: enqueue run_vapt_scan
  ORCH->>ORCH: CPU/RAM guard check
  ORCH->>ORCH: Nmap first
  ORCH->>ORCH: OpenVAS (Full and Fast, host=1)
  ORCH->>ORCH: Nuclei/ZAP/Nikto/SQLmap safe profiles
  ORCH->>DB: Save normalized findings
  ORCH->>DB: Update progress and completion
  API-->>UI: WebSocket/HTTP status updates
```

## 4) Bug Hunting Data Flow

```mermaid
sequenceDiagram
  participant UI as Frontend
  participant API as Backend
  participant Q as Redis/Celery
  participant ORCH as Orchestrator
  participant DB as PostgreSQL

  UI->>API: POST /hunting/sessions
  API->>Q: enqueue run_hunting_pipeline
  ORCH->>DB: Step1 subdomains
  ORCH->>DB: Step2 live hosts
  ORCH->>DB: Step3 crawl URLs
  ORCH->>DB: Step4 screenshots
  ORCH->>DB: Step5 nuclei findings
  ORCH->>DB: Step6 aggregate + baseline diff
  ORCH->>DB: Step7 optional notifications
  API-->>UI: streaming progress per step
```

## 5) Database ER Diagram

```mermaid
erDiagram
  users ||--o{ scans : owns
  users ||--o{ hunting_sessions : owns
  scans ||--o{ findings : contains
  scans ||--o{ scan_logs : logs
  hunting_sessions ||--o{ subdomains : discovers
  hunting_sessions ||--o{ live_hosts : probes
  hunting_sessions ||--o{ crawled_urls : crawls
  hunting_sessions ||--o{ screenshots : captures
  hunting_sessions ||--o{ hunting_findings : detects
  hunting_sessions ||--o{ js_secrets : extracts
  hunting_sessions ||--o{ discovered_parameters : maps
  hunting_sessions ||--o{ takeover_candidates : flags
  hunting_sessions ||--o{ cloud_assets : inventories
  hunting_sessions ||--o{ email_recon : enumerates
  hunting_sessions ||--o{ delta_baselines : snapshots
  users ||--o{ chat_history : chats
  users ||--o{ notification_configs : configures
```

## 6) Queue and Task Flow

- Queue names: `vapt`, `hunting`, `default`
- Worker strategy:
  - `vapt`: serial by policy (one scan target at a time)
  - `hunting`: one pipeline active by default
  - `default`: notifications, maintenance, feed updates
- Retries: exponential backoff with task-level idempotency keys
- Resume: pipeline step checkpoints in `hunting_sessions.current_step`

## 7) Network Topology

- `frontend-net`: internet-facing UI and reverse proxy traffic.
- `backend-net`: internal API/data plane, not internet exposed.
- `scan-net`: scanner containers and orchestrator execution network.
- Policy: tools do not directly access frontend network.

## 8) Security Model

- Mandatory JWT auth for all scanning endpoints.
- RBAC roles: `admin`, `user`.
- External target approval workflow required before execution.
- Scope allowlisting for root domains/CIDRs.
- Safe defaults: no auto exploitation, conservative rates/timeouts.
- Full audit logs on create/update/delete/start/cancel actions.
- API rate limiting at Nginx and application middleware.
