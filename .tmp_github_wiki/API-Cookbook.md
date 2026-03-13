# API Cookbook

## Authentication

Request:

POST /api/v1/auth/login

Body:
{
  "email": "admin@expl0v1n.local",
  "password": "ChangeMeOnFirstLogin!"
}

## Start VAPT Scan

POST /api/v1/scans

Body:
{
  "target": "example.com",
  "target_type": "domain",
  "tools_config": {
    "safe_mode": true
  }
}

## Start Bug Hunting Pipeline

POST /api/v1/hunting/sessions

Body:
{
  "root_domain": "example.com",
  "preset": "standard",
  "methods_config": {
    "enabled": true
  }
}

## Get Dashboard Stats

GET /api/v1/dashboard/stats

## Export Reports

- GET /api/v1/reports/vapt/{scan_id}/pdf
- GET /api/v1/reports/vapt/{scan_id}/json
- GET /api/v1/reports/hunting/{session_id}/pdf
- GET /api/v1/reports/hunting/{session_id}/json

## Configure Notifications

PUT /api/v1/notifications/config

Body:
{
  "provider": "telegram",
  "enabled": true,
  "bot_token": "<token>",
  "chat_id": "<chat_id>",
  "notify_scan_start": true,
  "notify_scan_complete": true,
  "notify_critical_findings": true
}
