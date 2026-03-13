"""AI Assistant chat endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.hunting import ChatHistory
from app.schemas.schemas import ChatRequest, ChatResponse
from app.core.auth import get_current_user

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI Security Assistant."""
    # Store user message
    user_msg = ChatHistory(
        user_id=current_user.id,
        scan_id=data.scan_id,
        session_id=data.session_id,
        role="user",
        content=data.message,
    )
    db.add(user_msg)
    await db.flush()

    # Call AI service
    from app.services.ai_client import get_ai_response
    ai_response = await get_ai_response(
        user_id=current_user.id,
        message=data.message,
        scan_id=data.scan_id,
        session_id=data.session_id,
        action=data.action,
    )

    # Store assistant response
    assistant_msg = ChatHistory(
        user_id=current_user.id,
        scan_id=data.scan_id,
        session_id=data.session_id,
        role="assistant",
        content=ai_response,
    )
    db.add(assistant_msg)
    await db.flush()

    return ChatResponse(message=ai_response)


@router.get("/chat/history")
async def get_chat_history(
    scan_id: int = None,
    session_id: int = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(ChatHistory).where(ChatHistory.user_id == current_user.id)
    if scan_id:
        query = query.where(ChatHistory.scan_id == scan_id)
    if session_id:
        query = query.where(ChatHistory.session_id == session_id)
    query = query.order_by(ChatHistory.created_at.desc()).limit(limit)

    result = await db.execute(query)
    chats = result.scalars().all()
    return [
        {"role": c.role, "content": c.content, "created_at": c.created_at.isoformat()}
        for c in reversed(chats)
    ]
