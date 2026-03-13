from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse

import tldextract

from app.core.config import get_settings

_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$")


@dataclass(frozen=True)
class NormalizedTarget:
    type: str  # ip|domain|url
    input: str
    normalized: str
    root_domain: str | None
    is_public: bool
    is_in_allowlist: bool


_tld = tldextract.TLDExtract(suffix_list_urls=None)


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


def _domain_root(host: str) -> tuple[str, bool]:
    ext = _tld(host)
    if ext.suffix:
        return f"{ext.domain}.{ext.suffix}".lower(), True
    return host.lower(), False


def _is_domain_allowlisted(host: str) -> bool:
    host = host.lower().strip(".")
    for root in _allowed_root_domains():
        if host == root or host.endswith(f".{root}"):
            return True
    return False


def _is_ip_allowlisted(ip: ipaddress._BaseAddress) -> bool:
    for net in _allowed_cidrs():
        if ip in net:
            return True
    return False


def normalize_target(target_input: str) -> NormalizedTarget:
    raw = target_input.strip()
    if not raw:
        raise ValueError("invalid_target")

    # URL
    parsed = urlparse(raw)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        host = parsed.hostname or ""
        if not host:
            raise ValueError("invalid_url")
        root, has_public_suffix = _domain_root(host)
        normalized = urlunparse(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path or "/",
                "",
                parsed.query,
                "",
            )
        )
        is_public = bool(has_public_suffix)
        is_in_allowlist = _is_domain_allowlisted(host)
        return NormalizedTarget(
            type="url",
            input=raw,
            normalized=normalized,
            root_domain=root,
            is_public=is_public,
            is_in_allowlist=is_in_allowlist,
        )

    # IP
    try:
        ip = ipaddress.ip_address(raw)
        is_public = bool(getattr(ip, "is_global", False))
        is_in_allowlist = _is_ip_allowlisted(ip)
        return NormalizedTarget(
            type="ip",
            input=raw,
            normalized=str(ip),
            root_domain=None,
            is_public=is_public,
            is_in_allowlist=is_in_allowlist,
        )
    except ValueError:
        pass

    # Domain
    host = raw.lower().strip(".")
    if not _DOMAIN_RE.match(host):
        raise ValueError("invalid_domain")
    root, has_public_suffix = _domain_root(host)
    is_public = bool(has_public_suffix)
    is_in_allowlist = _is_domain_allowlisted(host)
    return NormalizedTarget(
        type="domain",
        input=raw,
        normalized=host,
        root_domain=root,
        is_public=is_public,
        is_in_allowlist=is_in_allowlist,
    )


def enforce_scope(normalized: NormalizedTarget) -> None:
    settings = get_settings()

    if not normalized.is_in_allowlist:
        raise ValueError("target_out_of_scope")

    if normalized.is_public and not settings.allow_public_targets:
        raise ValueError("public_targets_disabled")

