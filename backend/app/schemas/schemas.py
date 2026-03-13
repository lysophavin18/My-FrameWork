"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# ── Auth ─────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Users ────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = "user"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# ── Scans (VAPT) ────────────────────────────────────────────

class ScanCreate(BaseModel):
    target: str = Field(max_length=500)
    target_type: str  # ip, domain, url
    tools_config: Optional[dict] = None

    @field_validator("target")
    @classmethod
    def validate_target(cls, v, info):
        v = v.strip()
        if not v:
            raise ValueError("Target cannot be empty")
        # Basic validation — orchestrator does deep validation
        if len(v) > 500:
            raise ValueError("Target too long")
        return v

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v):
        if v not in ("ip", "domain", "url"):
            raise ValueError("target_type must be ip, domain, or url")
        return v


class ScanResponse(BaseModel):
    id: int
    user_id: int
    scan_type: str
    target: str
    target_type: str
    status: str
    progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FindingResponse(BaseModel):
    id: int
    scan_id: int
    tool: str
    title: str
    description: Optional[str] = None
    severity: str
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    affected_component: Optional[str] = None
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    is_false_positive: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Bug Hunting ──────────────────────────────────────────────

class HuntingSessionCreate(BaseModel):
    root_domain: str = Field(max_length=500)
    preset: Optional[str] = None  # quick, standard, deep, full_hunter
    steps_config: Optional[dict] = None
    methods_config: Optional[dict] = None

    @field_validator("root_domain")
    @classmethod
    def validate_domain(cls, v):
        v = v.strip().lower()
        pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid domain format")
        return v

    @field_validator("preset")
    @classmethod
    def validate_preset(cls, v):
        if v and v not in ("quick", "standard", "deep", "full_hunter"):
            raise ValueError("Invalid preset")
        return v


class HuntingSessionResponse(BaseModel):
    id: int
    user_id: int
    root_domain: str
    status: str
    preset: Optional[str] = None
    current_step: Optional[str] = None
    progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubdomainResponse(BaseModel):
    id: int
    subdomain: str
    source: str
    ip_address: Optional[str] = None
    is_new: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LiveHostResponse(BaseModel):
    id: int
    url: str
    status_code: Optional[int] = None
    title: Optional[str] = None
    technologies: Optional[dict] = None
    content_length: Optional[int] = None
    is_alive: bool
    port: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScreenshotResponse(BaseModel):
    id: int
    url: str
    file_path: str
    http_status: Optional[int] = None
    page_title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HuntingFindingResponse(BaseModel):
    id: int
    tool: str
    template_id: Optional[str] = None
    title: str
    severity: str
    url: Optional[str] = None
    is_new: bool
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Notifications ────────────────────────────────────────────

class NotificationConfigUpdate(BaseModel):
    provider: str = "telegram"
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    enabled: bool = False
    notify_scan_start: bool = True
    notify_scan_complete: bool = True
    notify_critical_findings: bool = True
    notify_new_subdomains: bool = True
    notify_new_live_hosts: bool = True


class NotificationConfigResponse(BaseModel):
    id: int
    provider: str
    enabled: bool
    notify_scan_start: bool
    notify_scan_complete: bool
    notify_critical_findings: bool
    notify_new_subdomains: bool
    notify_new_live_hosts: bool

    class Config:
        from_attributes = True


# ── AI Assistant ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(max_length=4000)
    scan_id: Optional[int] = None
    session_id: Optional[int] = None
    action: Optional[str] = None  # explain, remediate, prioritize, summarize


class ChatResponse(BaseModel):
    message: str
    role: str = "assistant"


# ── Dashboard ────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_scans: int = 0
    active_scans: int = 0
    total_findings: int = 0
    severity_counts: dict[str, int] = Field(default_factory=dict)
    unique_cves: int = 0
    recent_scans: list[dict] = Field(default_factory=list)
    recent_hunting_sessions: list[dict] = Field(default_factory=list)
    total_findings: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    total_hunting_sessions: int = 0
    total_subdomains: int = 0
    total_live_hosts: int = 0
