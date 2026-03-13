from __future__ import annotations

import uuid

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class HuntingPipeline(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "hunting_pipelines"

    root_domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("queued", "running", "completed", "failed", "canceled", name="pipeline_status"),
        index=True,
        nullable=False,
    )
    requested_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)

    options: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class PipelineStep(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "pipeline_steps"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("queued", "running", "completed", "failed", "canceled", name="pipeline_status"),
        nullable=False,
    )
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str | None] = mapped_column(String(512), nullable=True)
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Subdomain(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "subdomains"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    tag: Mapped[str | None] = mapped_column(String(32), nullable=True)
    discovered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)


class LiveHost(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "live_hosts"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    subdomain_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subdomains.id"), index=True
    )

    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    is_live: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    technologies: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    content_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_seen_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)


class CrawledUrl(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "crawled_urls"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    live_host_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("live_hosts.id"), index=True
    )
    url: Mapped[str] = mapped_column(String(4096), nullable=False)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    params: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    discovered_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)


class Screenshot(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "screenshots"

    pipeline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hunting_pipelines.id"), index=True
    )
    live_host_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("live_hosts.id"), index=True
    )
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

