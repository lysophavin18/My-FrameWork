from __future__ import annotations

import time

import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()
client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)


async def enforce_rate_limit(user_id: int) -> None:
    minute = int(time.time() // 60)
    key = f"ai_rl:{user_id}:{minute}"
    current = await client.incr(key)
    if current == 1:
        await client.expire(key, 60)
    if current > settings.ai_rate_limit_per_minute:
        raise ValueError("ai_rate_limited")

