"""Notification configuration endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.hunting import NotificationConfig
from app.schemas.schemas import NotificationConfigUpdate, NotificationConfigResponse
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/config", response_model=NotificationConfigResponse)
async def get_notification_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NotificationConfig).where(NotificationConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="No notification config found")
    return config


@router.put("/config", response_model=NotificationConfigResponse)
async def update_notification_config(
    data: NotificationConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NotificationConfig).where(NotificationConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        config = NotificationConfig(user_id=current_user.id)
        db.add(config)

    for field, value in data.model_dump().items():
        setattr(config, field, value)

    await db.flush()
    await db.refresh(config)
    return config


@router.post("/test")
async def test_notification(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(NotificationConfig).where(NotificationConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    if not config or not config.enabled:
        raise HTTPException(status_code=400, detail="Notifications not configured or disabled")

    from app.services.task_dispatcher import dispatch_test_notification
    dispatch_test_notification(current_user.id)

    return {"status": "Test notification dispatched"}
