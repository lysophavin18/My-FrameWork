"""Startup tasks — create default admin user."""

import structlog
from sqlalchemy import select

from app.config import get_settings
from app.database import async_session
from app.core.auth import hash_password

logger = structlog.get_logger()
settings = get_settings()


async def create_default_admin():
    from app.models.user import User

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == settings.admin_email)
        )
        if result.scalar_one_or_none():
            logger.info("Default admin already exists")
            return

        admin = User(
            username=settings.admin_username,
            email=settings.admin_email,
            hashed_password=hash_password(settings.admin_password),
            role="admin",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        logger.info("Default admin user created", email=settings.admin_email)
