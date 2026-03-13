# Installation Guide

## System Requirements

### Minimum (Core profile)
- OS: Ubuntu 22.04 LTS or Debian 12 (Linux recommended)
- CPU: 8 vCPU
- RAM: 16 GB
- Disk: 120 GB SSD

### Recommended (Core + Hunting + Advanced + AI)
- OS: Ubuntu 24.04 LTS
- CPU: 16-24 vCPU
- RAM: 48-64 GB
- Disk: 500 GB NVMe SSD

## Prerequisites Checklist

- Docker Engine 24+
- Docker Compose v2+
- Git
- Python 3.11+ (optional for local scripts)
- 64-bit virtualization-enabled host

## Step-by-Step Installation

1. Clone repository
```bash
git clone https://github.com/your-org/expl0v1n-framework.git
cd expl0v1n-framework
```

2. Copy environment file
```bash
cp .env.example .env
```

3. Generate secrets
```bash
bash scripts/generate-secrets.sh
# copy output into .env
```

4. Pull/build images
```bash
docker compose --profile core build
```

5. Start services
```bash
docker compose --profile core up -d
# Optional:
# --profile hunting
# --profile advanced
# --profile ai
```

6. Access UI
- URL (via gateway): http://localhost
- API (via gateway): http://localhost/api/v1
- API (direct): http://127.0.0.1:8000/api/v1

8. Default admin
- Email: admin@expl0v1n.local
- Password: ChangeMeOnFirstLogin!
- First action: rotate password + enable MFA (if integrated)

## Environment Variables Reference

| Variable | Description |
|---|---|
| POSTGRES_PASSWORD | DB password |
| REDIS_PASSWORD | Redis password |
| JWT_SECRET_KEY | JWT signing secret |
| OPENVAS_PASSWORD | OpenVAS admin password |
| AI_API_URL | OpenAI-compatible endpoint |
| AI_API_KEY | LLM API key |
| AI_MODEL | Model name |
| TELEGRAM_BOT_TOKEN | Telegram bot token |
| TELEGRAM_CHAT_ID | Telegram destination chat |
| SCAN_CPU_THRESHOLD | Pause/queue scans above threshold |
| SCAN_RAM_THRESHOLD | Pause/queue scans above threshold |

## Troubleshooting

- `backend unhealthy`: verify DB/Redis credentials and healthchecks.
- `celery no workers`: ensure `celery-worker` container is running.
- `OpenVAS slow`: keep max concurrent scans at 1; run feed updates off-hours.
- `build fails for tool images`: check outbound internet and package mirrors.
- `AI chat error`: confirm API key, model name, and endpoint path.

## Updating / Upgrading

```bash
git pull
docker compose --profile core up -d --build
```

## Uninstall / Cleanup

```bash
docker compose down -v
# optional cleanup
# docker system prune -a
```
