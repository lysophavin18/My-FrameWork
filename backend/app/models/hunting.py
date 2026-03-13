"""Bug Hunting models — full recon pipeline data."""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class HuntingSession(Base):
    """A bug hunting recon session for a root domain."""
    __tablename__ = "hunting_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    root_domain = Column(String(500), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="pending")
    preset = Column(String(30), nullable=True)  # quick, standard, deep, full_hunter
    steps_config = Column(JSON, nullable=True)  # which steps/methods to run
    methods_config = Column(JSON, nullable=True)  # advanced method config
    current_step = Column(String(50), nullable=True)
    progress = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    subdomains = relationship("Subdomain", back_populates="session", cascade="all, delete-orphan")
    live_hosts = relationship("LiveHost", back_populates="session", cascade="all, delete-orphan")
    crawled_urls = relationship("CrawledURL", back_populates="session", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="session", cascade="all, delete-orphan")
    hunting_findings = relationship("HuntingFinding", back_populates="session", cascade="all, delete-orphan")


class Subdomain(Base):
    __tablename__ = "subdomains"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    subdomain = Column(String(500), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # subfinder, amass, assetfinder, crtsh, brute
    ip_address = Column(String(45), nullable=True)
    is_new = Column(Boolean, default=True)  # new compared to last scan
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("HuntingSession", back_populates="subdomains")


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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("HuntingSession", back_populates="live_hosts")


class CrawledURL(Base):
    __tablename__ = "crawled_urls"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    live_host_id = Column(Integer, ForeignKey("live_hosts.id"), nullable=True)
    url = Column(String(2000), nullable=False)
    source = Column(String(50), nullable=False)  # katana, gospider, waybackurls, gau
    category = Column(String(50), nullable=True)  # api, static, form, js, endpoint
    parameters = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("HuntingSession", back_populates="crawled_urls")


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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("HuntingSession", back_populates="screenshots")


class HuntingFinding(Base):
    """Findings from nuclei and other bug hunting tools."""
    __tablename__ = "hunting_findings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    tool = Column(String(50), nullable=False)
    template_id = Column(String(200), nullable=True)
    title = Column(String(500), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(2000), nullable=True)
    matched_at = Column(String(2000), nullable=True)
    curl_command = Column(Text, nullable=True)
    extracted_results = Column(JSON, nullable=True)
    is_new = Column(Boolean, default=True)
    cve_id = Column(String(50), nullable=True)
    cvss_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("HuntingSession", back_populates="hunting_findings")


# ── Advanced Method Results ──────────────────────────────────

class JSSecret(Base):
    """Secrets extracted from JavaScript files (Method 3)."""
    __tablename__ = "js_secrets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    js_url = Column(String(2000), nullable=False)
    secret_type = Column(String(100), nullable=False)  # api_key, jwt, db_string, etc.
    secret_value = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    context = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DiscoveredParameter(Base):
    """Parameters from Method 4."""
    __tablename__ = "discovered_parameters"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    url = Column(String(2000), nullable=False)
    parameter_name = Column(String(200), nullable=False)
    parameter_type = Column(String(50), nullable=True)  # numeric, url, file, search
    source = Column(String(50), nullable=False)  # arjun, paramspider, x8
    risk_level = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TakeoverCandidate(Base):
    """Subdomain takeover candidates (Method 5)."""
    __tablename__ = "takeover_candidates"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    subdomain = Column(String(500), nullable=False)
    cname_target = Column(String(500), nullable=True)
    service = Column(String(100), nullable=True)  # s3, heroku, github_pages, etc.
    confidence = Column(String(20), nullable=False)  # confirmed, likely, possible
    evidence = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CloudAsset(Base):
    """Cloud assets (Method 9)."""
    __tablename__ = "cloud_assets"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)  # s3, azure_blob, gcp_bucket, service
    asset_name = Column(String(500), nullable=False)
    provider = Column(String(50), nullable=True)  # aws, azure, gcp
    access_level = Column(String(50), nullable=True)  # public_read, public_write, private
    risk_rating = Column(String(20), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EmailRecon(Base):
    """Email reconnaissance (Method 14)."""
    __tablename__ = "email_recon"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    source = Column(String(50), nullable=False)  # theharvester, hunter, linkedin
    breach_count = Column(Integer, default=0)
    breaches = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DeltaBaseline(Base):
    """Baseline for delta/continuous scanning (Method 12)."""
    __tablename__ = "delta_baselines"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    root_domain = Column(String(500), nullable=False, index=True)
    baseline_type = Column(String(50), nullable=False)  # subdomains, ports, technologies
    baseline_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── AI Assistant ─────────────────────────────────────────────

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scan_id = Column(Integer, nullable=True)  # context scan
    session_id = Column(Integer, nullable=True)  # context hunting session
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ── Notifications ────────────────────────────────────────────

class NotificationConfig(Base):
    __tablename__ = "notification_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, default="telegram")
    bot_token = Column(String(500), nullable=True)
    chat_id = Column(String(100), nullable=True)
    enabled = Column(Boolean, default=False)
    notify_scan_start = Column(Boolean, default=True)
    notify_scan_complete = Column(Boolean, default=True)
    notify_critical_findings = Column(Boolean, default=True)
    notify_new_subdomains = Column(Boolean, default=True)
    notify_new_live_hosts = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
