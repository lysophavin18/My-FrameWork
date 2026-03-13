from __future__ import annotations

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()

        redis_client = getattr(request.app.state, "redis", None)
        if redis_client is None:
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or request.client.host

        minute = int(time.time() // 60)
        key = f"ratelimit:{user_id or ip}:{minute}"
        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, 60)

        if current > settings.api_rate_limit_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "rate_limited"},
            )

        return await call_next(request)

