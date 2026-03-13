from __future__ import annotations

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models.user import User
from app.db.session import SessionLocal


def ensure_default_admin() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        existing = db.execute(select(User).where(User.email == settings.default_admin_email)).scalar_one_or_none()
        if existing is not None:
            return

        admin = User(
            email=settings.default_admin_email,
            full_name="Default Admin",
            role="admin",
            is_active=True,
            password_hash=hash_password(settings.default_admin_password),
            must_change_password=True,
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()

