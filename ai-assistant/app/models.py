from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.db import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(String(500), nullable=False)
    status = Column(String(30), nullable=False)
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
    remediation = Column(Text, nullable=True)


class HuntingSession(Base):
    __tablename__ = "hunting_sessions"

    id = Column(Integer, primary_key=True, index=True)
    root_domain = Column(String(500), nullable=False, index=True)
    status = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)


class HuntingFinding(Base):
    __tablename__ = "hunting_findings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("hunting_sessions.id"), nullable=False, index=True)
    tool = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    severity = Column(String(20), nullable=False)
    url = Column(String(2000), nullable=True)
    cve_id = Column(String(50), nullable=True, index=True)

