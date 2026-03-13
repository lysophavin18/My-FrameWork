from __future__ import annotations

import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._mixins import UUIDPrimaryKeyMixin


class IDORFinding(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "idor_findings"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    endpoint: Mapped[str] = mapped_column(String(4096), nullable=False)
    risk: Mapped[str] = mapped_column(
        Enum("critical", "high", "medium", "low", "info", "unknown", name="severity"), nullable=False
    )
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    detected_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

