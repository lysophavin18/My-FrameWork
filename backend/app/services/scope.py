"""Scope enforcement utilities (allowlists + external target classification)."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

from app.config import get_settings

TargetType = Literal["ip", "domain", "url"]


_INTERNAL_TLDS = {
    "local",
    "internal",
    "localhost",
    "test",
    "example",
    "invalid",
}


@dataclass(frozen=True)
class TargetScope:
    normalized: str
    host: str | None
    root_domain: str | None
    is_public: bool
    is_in_allowlist: bool


def _allowed_root_domains() -> list[str]:
    settings = get_settings()
    return [d.strip().lower() for d in settings.allowed_root_domains.split(",") if d.strip()]


def _allowed_cidrs() -> list[ipaddress._BaseNetwork]:
    settings = get_settings()
    networks: list[ipaddress._BaseNetwork] = []
    for cidr in [c.strip() for c in settings.allowed_cidrs.split(",") if c.strip()]:
        try:
            networks.append(ipaddress.ip_network(cidr, strict=False))
        except ValueError:
            continue
    return networks


def _is_domain_allowlisted(host: str) -> bool:
    host = host.strip(".").lower()
    for root in _allowed_root_domains():
        if host == root or host.endswith(f".{root}"):
            return True
    return False


def _is_ip_allowlisted(ip: ipaddress._BaseAddress) -> bool:
    for net in _allowed_cidrs():
        if ip in net:
            return True
    return False


def _is_public_domain(host: str) -> bool:
    host = host.strip(".").lower()
    parts = host.split(".")
    if len(parts) < 2:
        return False
    tld = parts[-1]
    if tld in _INTERNAL_TLDS:
        return False
    return True


def classify_target(target: str, target_type: TargetType) -> TargetScope:
    raw = target.strip()
    if not raw:
        raise ValueError("invalid_target")

    if target_type == "url":
        parsed = urlparse(raw)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("invalid_url")
        host = (parsed.hostname or "").lower()
        if not host:
            raise ValueError("invalid_url")
        normalized = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{parsed.path or '/'}"
        is_public = _is_public_domain(host)
        is_in_allowlist = _is_domain_allowlisted(host)
        return TargetScope(
            normalized=normalized,
            host=host,
            root_domain=None,
            is_public=is_public,
            is_in_allowlist=is_in_allowlist,
        )

    if target_type == "ip":
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError as e:
            raise ValueError("invalid_ip") from e
        is_public = bool(getattr(ip, "is_global", False))
        is_in_allowlist = _is_ip_allowlisted(ip)
        return TargetScope(
            normalized=str(ip),
            host=None,
            root_domain=None,
            is_public=is_public,
            is_in_allowlist=is_in_allowlist,
        )

    if target_type == "domain":
        host = raw.strip(".").lower()
        is_public = _is_public_domain(host)
        is_in_allowlist = _is_domain_allowlisted(host)
        return TargetScope(
            normalized=host,
            host=host,
            root_domain=None,
            is_public=is_public,
            is_in_allowlist=is_in_allowlist,
        )

    raise ValueError("invalid_target_type")


def enforce_scope(scope: TargetScope) -> None:
    settings = get_settings()

    if not scope.is_in_allowlist:
        raise ValueError("target_out_of_scope")
    if scope.is_public and not settings.allow_public_targets:
        raise ValueError("public_targets_disabled")

