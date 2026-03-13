"""Middleware for audit logging and rate limiting."""

import time
import structlog
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings
from app.core.auth import decode_token
from app.database import async_session
from app.models.scan import AuditLog
import redis.asyncio as redis

logger = structlog.get_logger()
settings = get_settings()


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Logs every API request for audit trail."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)

        user_id = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = decode_token(token)
                user_id = int(payload.get("sub")) if payload.get("sub") else None
            except Exception:
                user_id = None

        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        logger.info(
            "api_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
            client_ip=client_ip,
            user_agent=user_agent,
            user_id=user_id,
        )

        try:
            async with async_session() as session:
                session.add(
                    AuditLog(
                        user_id=user_id,
                        action="api_request",
                        resource_type="http",
                        resource_id=None,
                        details={
                            "method": request.method,
                            "path": request.url.path,
                            "status": response.status_code,
                            "duration_ms": duration_ms,
                            "user_agent": user_agent,
                        },
                        ip_address=client_ip,
                    )
                )
                await session.commit()
        except Exception:
            logger.exception("audit_log_write_failed")

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory sliding window rate limiter."""

    def __init__(self, app):
        super().__init__(app)
        self._redis = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "0.0.0.0"
        now = time.time()
        window = int(settings.rate_limit_window_seconds)
        max_requests = int(settings.rate_limit_requests)

        bucket = int(now // window)
        key = f"ratelimit:{client_ip}:{bucket}"
        try:
            current = await self._redis.incr(key)
            if current == 1:
                await self._redis.expire(key, window)
            if current > max_requests:
                logger.warning("rate_limit_exceeded", client_ip=client_ip)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again later."},
                    headers={"Retry-After": str(window)},
                )
        except Exception:
            logger.exception("rate_limit_redis_failed")

        return await call_next(request)
