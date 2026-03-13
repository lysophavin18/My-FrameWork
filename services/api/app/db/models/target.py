from __future__ import annotations

import uuid

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class Target(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "targets"

    type: Mapped[str] = mapped_column(Enum("ip", "domain", "url", name="target_type"), nullable=False)
    input: Mapped[str] = mapped_column(String(2048), nullable=False)
    normalized: Mapped[str] = mapped_column(String(2048), nullable=False)
    root_domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_in_allowlist: Mapped[bool] = mapped_column(Boolean, nullable=False)

    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_note: Mapped[str | None] = mapped_column(String(500), nullable=True)

