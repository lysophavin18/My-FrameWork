# Advanced Methods

Expl0V1N includes 15 opt-in advanced bug hunting methods.

## Method Summary

1. Subdomain permutation and brute-force
2. ASN and CIDR range discovery
3. JavaScript analysis and secret extraction
4. Parameter discovery and fuzzing
5. Subdomain takeover detection
6. Technology fingerprinting and CVE matching
7. CORS and security header misconfiguration checks
8. API endpoint fuzzing and discovery
9. Cloud asset discovery
10. SSRF and open redirect fast checks
11. Broken access control and IDOR detection
12. Continuous monitoring and delta scans
13. Favicon hash and Shodan enrichment
14. Email and credential reconnaissance
15. One-liner fast recon chains

## Operational Guidance

- Keep all methods opt-in by default.
- Enforce strict scope checks before each step.
- Apply per-tool rate limits to avoid disruption.
- Persist each stage output independently for resume support.
- Use deduplication and TTL cache to control runtime cost.
