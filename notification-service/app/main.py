"""Notification service for Telegram and future providers."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="Expl0V1N Notification Service", version="1.0.0")


class TelegramMessage(BaseModel):
    bot_token: str
    chat_id: str
    text: str
    parse_mode: str = "Markdown"


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service"}


@app.post("/telegram/send")
async def send_telegram(message: TelegramMessage):
    url = f"https://api.telegram.org/bot{message.bot_token}/sendMessage"
    payload = {
        "chat_id": message.chat_id,
        "text": message.text,
        "parse_mode": message.parse_mode,
        "disable_web_page_preview": True,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return {"status": "sent"}


@app.post("/telegram/test")
async def test_telegram():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise HTTPException(status_code=400, detail="TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing")

    payload = TelegramMessage(
        bot_token=token,
        chat_id=chat_id,
        text="✅ Expl0V1N test notification successful.",
    )
    return await send_telegram(payload)
