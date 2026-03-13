"""Client for AI Assistant microservice."""

import os
import httpx
from typing import Optional

AI_ASSISTANT_URL = os.getenv("AI_ASSISTANT_URL", "http://ai-assistant:8001")


async def get_ai_response(
    user_id: int,
    message: str,
    scan_id: Optional[int] = None,
    session_id: Optional[int] = None,
    action: Optional[str] = None,
) -> str:
    payload = {
        "user_id": user_id,
        "message": message,
        "scan_id": scan_id,
        "session_id": session_id,
        "action": action,
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{AI_ASSISTANT_URL}/v1/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("answer", "No answer returned by AI service.")
    except Exception as exc:
        return (
            "AI service is currently unavailable. "
            f"Please try again later. (Error: {exc})"
        )
