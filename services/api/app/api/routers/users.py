from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.user import ResetPasswordRequest, UserCreateRequest, UserOut, UserUpdateRequest
from app.services import users as users_service

router = APIRouter()


@router.post("", response_model=UserOut, dependencies=[Depends(require_admin)])
def create_user(payload: UserCreateRequest, db: Session = Depends(get_db)):
    user = users_service.create_user(
        db=db,
        email=str(payload.email),
        full_name=payload.full_name,
        role=payload.role,
        password=payload.password,
    )
    db.commit()
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        must_change_password=user.must_change_password,
    )


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    users = users_service.list_users(db=db)
    return [
        UserOut(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
            must_change_password=u.must_change_password,
        )
        for u in users
    ]


@router.patch("/{user_id}", response_model=UserOut, dependencies=[Depends(require_admin)])
def update_user(user_id: uuid.UUID, payload: UserUpdateRequest, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")

    users_service.update_user(
        db=db,
        user=user,
        full_name=payload.full_name if payload.full_name is not None else users_service.UNSET,
        is_active=payload.is_active if payload.is_active is not None else users_service.UNSET,
        role=payload.role if payload.role is not None else users_service.UNSET,
    )
    db.commit()
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        must_change_password=user.must_change_password,
    )


@router.post("/{user_id}/reset-password", response_model=UserOut, dependencies=[Depends(require_admin)])
def reset_password(user_id: uuid.UUID, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not_found")

    users_service.reset_password(db=db, user=user, new_password=payload.new_password)
    db.commit()
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        must_change_password=user.must_change_password,
    )

