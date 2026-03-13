from __future__ import annotations

import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._mixins import UUIDPrimaryKeyMixin


class Finding(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "findings"

    scan_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id"), index=True)
    pipeline_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )

    tool: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    severity: Mapped[str] = mapped_column(
        Enum("critical", "high", "medium", "low", "info", "unknown", name="severity"),
        index=True,
        nullable=False,
    )
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cve_id: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)

    affected_host: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    affected_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    dedup_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    first_seen_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

