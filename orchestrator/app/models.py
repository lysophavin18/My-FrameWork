from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)

from app.db import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    scan_type = Column(String(20), nullable=False)
    target = Column(String(500), nullable=False)
    target_type = Column(String(20), nullable=False)
    status = Column(String(30), nullable=False, default="pending")
    progress = Column(Integer, default=0)
    tools_config = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), nullable=True)


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)
    tool = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)
    cvss_score = Column(Float, nullable=True)
    cve_id = Column(String(50), nullable=True, index=True)
    cwe_id = Column(String(50), nullable=True)
    affected_component = Column(String(500), nullable=True)
    evidence = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    raw_output = Column(JSON, nullable=True)
    is_false_positive = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), nullable=True)


class ScanLog(Base):
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)
    level = Column(String(20), nullable=False, default="info")
    tool = Column(String(50), nullable=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=True)


class HuntingSession(Base):
    __tablename__ = "hunting_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    root_domain = Column(String(500), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="pending")
    preset = Column(String(30), nullable=True)
    steps_config = Column(JSON, nullable=True)
    methods_config = Column(JSON, nullable=True)
    current_step = Column(String(50), nullable=True)
    progress = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)


class Subdomain(Base):
    __tablename__ = "subdomains"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    subdomain = Column(String(500), nullable=False, index=True)
    source = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    is_new = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=True)


class LiveHost(Base):
    __tablename__ = "live_hosts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    subdomain_id = Column(Integer, ForeignKey("subdomains.id"), nullable=True)
    url = Column(String(1000), nullable=False)
    status_code = Column(Integer, nullable=True)
    title = Column(String(500), nullable=True)
    technologies = Column(JSON, nullable=True)
    content_length = Column(Integer, nullable=True)
    is_alive = Column(Boolean, default=True)
    port = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)


class CrawledURL(Base):
    __tablename__ = "crawled_urls"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    live_host_id = Column(Integer, ForeignKey("live_hosts.id"), nullable=True)
    url = Column(String(2000), nullable=False)
    source = Column(String(50), nullable=False)
    category = Column(String(50), nullable=True)
    parameters = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)


class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    live_host_id = Column(Integer, ForeignKey("live_hosts.id"), nullable=True)
    url = Column(String(1000), nullable=False)
    file_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    http_status = Column(Integer, nullable=True)
    page_title = Column(String(500), nullable=True)
    technologies = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)


class HuntingFinding(Base):
    __tablename__ = "hunting_findings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    tool = Column(String(50), nullable=False)
    template_id = Column(String(200), nullable=True)
    title = Column(String(500), nullable=False)
    severity = Column(String(20), nullable=False)
    url = Column(String(2000), nullable=True)
    is_new = Column(Boolean, default=True)
    cve_id = Column(String(50), nullable=True, index=True)
    cvss_score = Column(Float, nullable=True)
    raw_output = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)

