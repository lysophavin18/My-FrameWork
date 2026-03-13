from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, Field


class TargetCreateRequest(BaseModel):
    input: str = Field(min_length=1, max_length=2048)


class TargetApproveRequest(BaseModel):
    note: str | None = Field(default=None, max_length=500)


class TargetOut(BaseModel):
    id: uuid.UUID
    type: str
    input: str
    normalized: str
    root_domain: str | None
    is_public: bool
    is_in_allowlist: bool
    approved: bool
    approved_by: uuid.UUID | None
    approved_at: dt.datetime | None
    approval_note: str | None
    created_by: uuid.UUID
    created_at: dt.datetime

