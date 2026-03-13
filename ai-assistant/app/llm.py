from __future__ import annotations

import httpx

from app.config import get_settings

settings = get_settings()


def _chat_completions_url() -> str:
    base = str(settings.ai_api_url).rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


async def chat(*, system: str, user: str) -> str:
    url = _chat_completions_url()
    headers = {}
    if settings.ai_api_key:
        headers["Authorization"] = f"Bearer {settings.ai_api_key}"

    payload = {
        "model": settings.ai_model,
        "temperature": settings.ai_temperature,
        "max_tokens": settings.ai_max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return (data["choices"][0]["message"]["content"] or "").strip()

