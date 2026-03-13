from __future__ import annotations

import datetime as dt
import hashlib
import os


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

