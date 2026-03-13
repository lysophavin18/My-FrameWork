from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None = None
    role: str
    is_active: bool
    must_change_password: bool


class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=200)
    role: str = Field(pattern="^(admin|user)$")
    password: str = Field(min_length=12, max_length=200)


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=200)
    is_active: bool | None = None
    role: str | None = Field(default=None, pattern="^(admin|user)$")


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(min_length=12, max_length=200)

