# Bug Hunting Mode

## Pipeline Overview

Bug hunting runs as staged pipeline where each step feeds the next:

1. Subdomain discovery
2. Live host detection
3. URL crawling and endpoint extraction
4. Screenshot capture
5. Template vulnerability scanning
6. Aggregation and reporting
7. Optional notifications

## Key Outputs

- Subdomain inventory
- Live/dead host ratio
- Endpoint map with parameters
- Screenshot gallery
- Nuclei findings correlated to host and URL
- Delta report against prior sessions

## Runtime Defaults

- One hunting pipeline at a time
- Tool concurrency default: 10
- httpx timeout: 10s
- nuclei rate limit: 150 requests/sec
- Screenshot concurrency: 5 browsers

## Presets

- Quick Recon: subfinder -> httpx -> nuclei critical/high
- Standard Recon: passive recon + crawl + full nuclei + screenshots
- Deep Recon: advanced methods enabled, broader coverage
- Full Hunter: full optional chain with maximum depth
