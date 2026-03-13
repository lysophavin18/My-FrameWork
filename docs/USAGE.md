# Usage Guide

## Getting Started

1. Sign in as admin/user.
2. Verify target scope/approval status.
3. Choose mode: `VAPT` or `Bug Hunting`.

## VAPT Mode: Single Target Scan

1. Open Dashboard -> VAPT.
2. Enter exactly one target (IP/domain/URL).
3. Select safe tool profile.
4. Start scan.
5. Watch progress and logs in real-time.
6. Review findings by severity/CVE/tool.
7. Export PDF/JSON report.

## Bug Hunting Mode: Recon Pipeline

1. Open Dashboard -> Bug Hunting.
2. Input root domain.
3. Select steps (or choose preset):
   - Quick Recon
   - Standard Recon
   - Deep Recon
   - Full Hunter
4. Optionally enable Telegram notifications.
5. Start pipeline and monitor per-step progress.
6. Drill down subdomain -> host -> URL -> finding.
7. Export PDF/JSON and compare with previous scan (diff).

## Dashboard and Reports

- Severity donut/chart and counts by level.
- CVE totals and tool distribution.
- Live/dead host ratio and trend charts.
- Historical scan runs with state transitions.

## Telegram Notifications Setup

1. Settings -> Notifications.
2. Provider: Telegram.
3. Add bot token + chat ID.
4. Select triggers:
   - Scan start/complete/fail
   - New subdomains
   - Critical/high findings
   - New live hosts
5. Click Test Notification.

## User and Role Management

- Admin can create/deactivate users and assign roles.
- Users can run scans only within permitted scope.

## Report Export

- VAPT: `/reports/vapt/{scan_id}/pdf` and `/json`
- Hunting: `/reports/hunting/{session_id}/pdf` and `/json`

## API Examples

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@expl0v1n.local","password":"ChangeMeOnFirstLogin!"}'

# Start VAPT scan
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"target":"example.com","target_type":"domain"}'

# Start bug hunting pipeline
curl -X POST http://localhost:8000/api/v1/hunting/sessions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"root_domain":"example.com","preset":"standard"}'
```
