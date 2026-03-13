from __future__ import annotations

import secrets
import time
import uuid
from dataclasses import dataclass

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    refresh_jti: str
    access_expires_in: int
    refresh_expires_in: int


def _now() -> int:
    return int(time.time())


def _encode(payload: dict) -> str:
    settings = get_settings()
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_token_pair(user_id: uuid.UUID, role: str) -> TokenPair:
    settings = get_settings()
    issued_at = _now()
    access_exp = issued_at + settings.jwt_access_ttl_seconds
    refresh_exp = issued_at + settings.jwt_refresh_ttl_seconds
    refresh_jti = secrets.token_hex(16)

    access_payload = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": issued_at,
        "exp": access_exp,
        "sub": str(user_id),
        "role": role,
        "typ": "access",
    }
    refresh_payload = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": issued_at,
        "exp": refresh_exp,
        "sub": str(user_id),
        "role": role,
        "typ": "refresh",
        "jti": refresh_jti,
    }

    return TokenPair(
        access_token=_encode(access_payload),
        refresh_token=_encode(refresh_payload),
        refresh_jti=refresh_jti,
        access_expires_in=settings.jwt_access_ttl_seconds,
        refresh_expires_in=settings.jwt_refresh_ttl_seconds,
    )


def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
    except JWTError as e:
        raise ValueError("invalid_token") from e

