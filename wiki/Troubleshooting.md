# Troubleshooting

## Backend Unhealthy

- Confirm PostgreSQL and Redis credentials.
- Check backend logs for startup migration errors.
- Validate network reachability to db and redis.

## Jobs Stuck in Queue

- Verify celery-worker is running.
- Ensure broker URL and Redis password match.
- Confirm queue names align with task routing.

## OpenVAS Slow or Hanging

- Keep max concurrent OpenVAS scans at 1.
- Run feed updates outside active scan windows.
- Limit host and port scope.

## Empty Bug Hunting Results

- Confirm target domain is valid.
- Check DNS resolver file health.
- Validate outbound network policies for recon containers.

## AI Assistant Errors

- Validate AI_API_URL and AI_API_KEY.
- Confirm selected model exists on provider.
- Check AI rate limit settings.

## UI Not Loading

- Confirm nginx gateway is healthy.
- Check frontend build and API base URL.
- Verify CORS settings in backend.
