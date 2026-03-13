from __future__ import annotations

import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._mixins import UUIDPrimaryKeyMixin


class CloudAsset(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "cloud_assets"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    identifier: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    access_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    risk: Mapped[str] = mapped_column(
        Enum("critical", "high", "medium", "low", "info", "unknown", name="severity"), nullable=False
    )
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    discovered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

