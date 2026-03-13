from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.security import create_token_pair, decode_token, verify_password
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User


def login(db: Session, email: str, password: str):
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None or not user.is_active:
        raise ValueError("invalid_credentials")
    if not verify_password(password, user.password_hash):
        raise ValueError("invalid_credentials")

    token_pair = create_token_pair(user_id=user.id, role=user.role)
    expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=token_pair.refresh_expires_in)
    db.add(
        RefreshToken(
            user_id=user.id,
            token_jti=token_pair.refresh_jti,
            expires_at=expires_at,
        )
    )
    db.execute(update(User).where(User.id == user.id).values(last_login_at=dt.datetime.now(dt.timezone.utc)))
    db.flush()
    return user, token_pair


def refresh(db: Session, refresh_token: str):
    payload = decode_token(refresh_token)
    if payload.get("typ") != "refresh":
        raise ValueError("invalid_token_type")

    user_id = uuid.UUID(payload["sub"])
    jti = payload.get("jti")
    if not jti:
        raise ValueError("invalid_refresh_token")

    token_row = db.execute(select(RefreshToken).where(RefreshToken.token_jti == jti)).scalar_one_or_none()
    if token_row is None or token_row.revoked_at is not None:
        raise ValueError("refresh_token_revoked")
    if token_row.expires_at <= dt.datetime.now(dt.timezone.utc):
        raise ValueError("refresh_token_expired")

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None or not user.is_active:
        raise ValueError("inactive_user")

    token_row.revoked_at = dt.datetime.now(dt.timezone.utc)
    token_pair = create_token_pair(user_id=user.id, role=user.role)
    expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=token_pair.refresh_expires_in)
    db.add(RefreshToken(user_id=user.id, token_jti=token_pair.refresh_jti, expires_at=expires_at))
    db.flush()
    return user, token_pair


def logout(db: Session, refresh_token: str) -> None:
    payload = decode_token(refresh_token)
    if payload.get("typ") != "refresh":
        return
    jti = payload.get("jti")
    if not jti:
        return

    token_row = db.execute(select(RefreshToken).where(RefreshToken.token_jti == jti)).scalar_one_or_none()
    if token_row is None:
        return
    token_row.revoked_at = dt.datetime.now(dt.timezone.utc)
    db.flush()

