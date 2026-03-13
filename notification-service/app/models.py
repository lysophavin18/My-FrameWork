from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.db import Base


class NotificationConfig(Base):
    __tablename__ = "notification_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    provider = Column(String(50), nullable=False, default="telegram")
    bot_token = Column(String(500), nullable=True)
    chat_id = Column(String(100), nullable=True)
    enabled = Column(Boolean, default=False)
    notify_scan_start = Column(Boolean, default=True)
    notify_scan_complete = Column(Boolean, default=True)
    notify_critical_findings = Column(Boolean, default=True)
    notify_new_subdomains = Column(Boolean, default=True)
    notify_new_live_hosts = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

