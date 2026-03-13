"""Fast recon presets for bug hunting mode."""

PRESETS = {
    "quick": {
        "name": "QUICK RECON",
        "estimated_time": "< 5 min",
        "resource_profile": "low",
        "steps": [
            "subdomain_discovery",
            "live_host_detection",
            "nuclei_scan_critical_high",
        ],
    },
    "standard": {
        "name": "STANDARD RECON",
        "estimated_time": "< 30 min",
        "resource_profile": "medium",
        "steps": [
            "subdomain_discovery",
            "live_host_detection",
            "url_crawling",
            "nuclei_scan_all",
            "screenshot_capture",
        ],
    },
    "deep": {
        "name": "DEEP RECON",
        "estimated_time": "< 2 hours",
        "resource_profile": "high",
        "steps": [
            "subdomain_discovery",
            "subdomain_permutation",
            "asn_cidr_discovery",
            "live_host_detection",
            "url_crawling",
            "javascript_analysis",
            "parameter_discovery",
            "takeover_detection",
            "tech_fingerprint",
            "cors_headers_misconfig",
            "api_fuzzing",
            "nuclei_scan_all",
            "screenshot_capture",
        ],
    },
    "full_hunter": {
        "name": "FULL HUNTER",
        "estimated_time": "< 6 hours",
        "resource_profile": "very_high",
        "steps": [
            "all_methods_1_to_15",
        ],
    },
}
