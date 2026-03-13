from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.context import build_context
from app.llm import chat
from app.rate_limit import enforce_rate_limit
from app.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Expl0V1N AI Assistant", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        await enforce_rate_limit(payload.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=429, detail=str(exc))

    ctx = build_context(scan_id=payload.scan_id, session_id=payload.session_id)
    system = (
        "You are a security assistant for authorized defensive testing. "
        "Explain findings clearly, prioritize by risk, and provide safe remediation steps. "
        "Do not provide instructions for unauthorized exploitation."
    )
    user = payload.message
    if ctx:
        user = f"Context:\n{ctx}\n\nUser request:\n{payload.message}"

    try:
        answer = await chat(system=system, user=user)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"llm_error: {exc}")

    return ChatResponse(answer=answer)

