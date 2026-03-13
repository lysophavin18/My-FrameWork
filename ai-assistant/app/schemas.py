from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: int
    message: str = Field(min_length=1, max_length=4000)
    scan_id: int | None = None
    session_id: int | None = None
    action: str | None = None  # explain|remediate|prioritize|summarize|freeform


class ChatResponse(BaseModel):
    answer: str

