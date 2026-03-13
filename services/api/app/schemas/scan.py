from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, Field


class ScanCreateRequest(BaseModel):
    target_id: uuid.UUID
    label: str | None = Field(default=None, max_length=120)


class ScanOut(BaseModel):
    id: uuid.UUID
    target_id: uuid.UUID
    status: str
    requested_by: uuid.UUID
    started_at: dt.datetime | None = None
    finished_at: dt.datetime | None = None
    summary: dict
    created_at: dt.datetime


class ScanStepOut(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    progress: int
    message: str | None = None
    started_at: dt.datetime | None = None
    finished_at: dt.datetime | None = None


class ScanDetailOut(ScanOut):
    steps: list[ScanStepOut]

