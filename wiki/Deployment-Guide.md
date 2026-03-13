# Deployment Guide

## Minimum Infrastructure

- 8 vCPU
- 16 GB RAM
- 120 GB SSD
- Linux host with Docker Engine + Compose

## Recommended Infrastructure

- 16-24 vCPU
- 48-64 GB RAM
- 500 GB NVMe SSD
- Dedicated VM or isolated Kubernetes node group

## Deployment Steps

1. Clone repository.
2. Copy .env.example to .env.
3. Generate secrets.
4. Build images.
5. Run database migrations.
6. Start compose profiles.
7. Validate health endpoints.

## Compose Profiles

- core: API, frontend, db, redis, orchestrator, base scanners
- hunting: bug hunting service containers
- advanced: advanced fast hunting containers
- ai: AI assistant service

## Hardening Checklist

- Rotate all credentials before first run
- Enforce TLS at gateway
- Restrict target scope through approvals
- Lock outbound traffic where possible
- Configure backup and retention policies
