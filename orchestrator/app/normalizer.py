"""Normalize findings into consistent severity/CVE/CVSS schema."""

from typing import Any


def normalize_severity(value: str | None) -> str:
    if not value:
        return "info"
    v = value.lower().strip()
    mapping = {
        "critical": "critical",
        "high": "high",
        "medium": "medium",
        "moderate": "medium",
        "low": "low",
        "info": "info",
        "informational": "info",
    }
    return mapping.get(v, "info")


def cvss_to_severity(score: float | None) -> str:
    if score is None:
        return "info"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    if score > 0:
        return "low"
    return "info"


def normalize_nuclei_finding(item: dict[str, Any]) -> dict[str, Any]:
    info = item.get("info", {})
    classification = info.get("classification", {})
    cvss = classification.get("cvss-score")

    return {
        "tool": "nuclei",
        "title": info.get("name", item.get("template-id", "Nuclei Finding")),
        "description": info.get("description") or item.get("matched-at"),
        "severity": normalize_severity(info.get("severity") or cvss_to_severity(cvss)),
        "cvss_score": float(cvss) if cvss else None,
        "cve_id": (classification.get("cve-id") or [None])[0] if isinstance(classification.get("cve-id"), list) else classification.get("cve-id"),
        "evidence": item.get("matched-at"),
        "raw_output": item,
    }
