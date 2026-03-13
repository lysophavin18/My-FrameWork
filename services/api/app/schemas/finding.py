from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel


class FindingOut(BaseModel):
    id: uuid.UUID
    tool: str
    title: str
    severity: str
    cvss_score: float | None = None
    cve_id: str | None = None
    affected_host: str | None = None
    affected_url: str | None = None
    description: str | None = None
    evidence: dict
    tags: list
    first_seen_at: dt.datetime
    last_seen_at: dt.datetime

