# Production Checklist

## Security

- Enforce scope allowlists (`ALLOWED_ROOT_DOMAINS`, `ALLOWED_CIDRS`) and keep `ALLOW_PUBLIC_TARGETS=false` unless explicitly required.
- Require admin approval for all public targets (`pending_approval` workflow).
- Run behind TLS (terminate at your ingress or extend `nginx` with certs in `nginx/ssl/`).
- Store secrets in a proper secret manager (not in `.env`), rotate regularly.
- Restrict Docker socket access (prefer a socket proxy and dedicated worker node).
- Keep containers on segmented networks; avoid attaching DB/Redis to networks that have outbound access.

## Reliability

- Enable backups for PostgreSQL volumes and validate restore procedures.
- Add Alembic migrations for schema evolution (the scaffold uses `create_all` for initial bootstrap).
- Pin tool versions (avoid `@latest` in tool Dockerfiles for reproducible builds).
- Use healthchecks and restart policies for core services.

## Performance

- Keep OpenVAS concurrency at 1 and schedule feed updates off-hours.
- Increase Postgres/Redis resources for large hunting pipelines.
- Use conservative defaults (timeouts, concurrency) and only enable advanced modules when needed.

## Observability

- Centralize logs (Loki/ELK) and include request IDs.
- Add metrics (Prometheus) for queue depth, scan durations, error rates.
- Track tool runtime per step and enforce per-step timeouts.

