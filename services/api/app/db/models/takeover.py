from __future__ import annotations

import uuid

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._mixins import UUIDPrimaryKeyMixin


class TakeoverCandidate(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "takeovers"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    subdomain_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subdomains.id"), index=True
    )
    provider: Mapped[str | None] = mapped_column(String(128), nullable=True)
    confidence: Mapped[str] = mapped_column(String(32), nullable=False)
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    detected_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

