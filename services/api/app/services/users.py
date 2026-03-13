from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models.user import User


UNSET = object()


def create_user(db: Session, *, email: str, full_name: str | None, role: str, password: str) -> User:
    email_norm = email.lower().strip()
    existing = db.execute(select(User).where(User.email == email_norm)).scalar_one_or_none()
    if existing is not None:
        raise ValueError("email_already_exists")

    user = User(
        email=email_norm,
        full_name=full_name,
        role=role,
        is_active=True,
        password_hash=hash_password(password),
        must_change_password=True,
    )
    db.add(user)
    db.flush()
    return user


def list_users(db: Session) -> list[User]:
    return list(db.execute(select(User).order_by(User.created_at.desc())).scalars().all())


def update_user(
    db: Session,
    *,
    user: User,
    full_name: str | None | object = UNSET,
    is_active: bool | None | object = UNSET,
    role: str | None | object = UNSET,
) -> User:
    if full_name is not UNSET:
        user.full_name = full_name  # type: ignore[assignment]
    if is_active is not UNSET:
        user.is_active = bool(is_active)  # type: ignore[arg-type]
    if role is not UNSET and role is not None:
        user.role = role
    db.flush()
    return user


def reset_password(db: Session, *, user: User, new_password: str) -> User:
    user.password_hash = hash_password(new_password)
    user.must_change_password = True
    db.flush()
    return user
