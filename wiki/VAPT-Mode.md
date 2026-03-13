# VAPT Mode

## Purpose

Run a controlled, single-target vulnerability assessment and penetration testing workflow.

## Input Rules

- Exactly one target per scan
- Allowed types: IP, domain, URL
- Validation is required before enqueue

## Execution Sequence

1. Validate target and user permissions.
2. Check CPU and RAM threshold.
3. Queue if system is busy.
4. Run Nmap first for service discovery.
5. Feed discovery to OpenVAS and web scanners.
6. Run OpenVAS with Full and Fast profile.
7. Restrict OpenVAS host count to 1.
8. Run Nuclei, ZAP, Nikto, SQLmap in safe mode.
9. Normalize CVEs/CVSS/severity.
10. Persist findings and generate reports.

## Safety Defaults

- No automatic exploitation
- SQLmap non-aggressive policy
- Controlled timeout and rate limits
- Explicit approvals for external targets
