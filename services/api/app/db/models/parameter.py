from __future__ import annotations

import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._mixins import UUIDPrimaryKeyMixin


class DiscoveredParameter(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "parameters"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    crawled_url_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crawled_urls.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    kind: Mapped[str | None] = mapped_column(String(64), nullable=True)
    risk: Mapped[str] = mapped_column(
        Enum("critical", "high", "medium", "low", "info", "unknown", name="severity"), nullable=False
    )
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    discovered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

