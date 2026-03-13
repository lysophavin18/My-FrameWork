from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, Field


class HuntingPipelineCreateRequest(BaseModel):
    root_domain: str = Field(min_length=1, max_length=255)
    steps: list[str] = Field(
        default_factory=lambda: ["subdomains", "live_hosts", "crawl", "screenshots", "nuclei"]
    )
    options: dict = Field(default_factory=dict)


class HuntingPipelineOut(BaseModel):
    id: uuid.UUID
    root_domain: str
    status: str
    requested_by: uuid.UUID
    options: dict
    started_at: dt.datetime | None = None
    finished_at: dt.datetime | None = None
    summary: dict
    created_at: dt.datetime


class PipelineStepOut(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    progress: int
    message: str | None = None
    started_at: dt.datetime | None = None
    finished_at: dt.datetime | None = None


class HuntingPipelineDetailOut(HuntingPipelineOut):
    steps: list[PipelineStepOut]


class SubdomainOut(BaseModel):
    id: uuid.UUID
    name: str
    source: str
    tag: str | None = None
    discovered_at: dt.datetime


class LiveHostOut(BaseModel):
    id: uuid.UUID
    url: str
    is_live: bool
    status_code: int | None = None
    title: str | None = None
    technologies: list
    content_length: int | None = None
    last_seen_at: dt.datetime


class CrawledUrlOut(BaseModel):
    id: uuid.UUID
    url: str
    category: str | None = None
    params: dict
    discovered_at: dt.datetime


class ScreenshotOut(BaseModel):
    id: uuid.UUID
    path: str
    sha256: str
    meta: dict
    created_at: dt.datetime

