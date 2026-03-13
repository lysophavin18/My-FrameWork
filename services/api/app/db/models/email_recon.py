from __future__ import annotations

import uuid

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._mixins import UUIDPrimaryKeyMixin


class EmailRecon(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "email_recon"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    breach_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    discovered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

