# Operations Runbook

## Daily Checks

- Verify service health endpoints
- Check queue depth and worker status
- Review failed scan/pipeline tasks
- Review high severity alerts

## Weekly Checks

- Validate backups and restore test
- Review scanner template updates
- Rotate temporary tokens and stale credentials
- Rebuild images with patched base layers

## Incident Playbook

1. Identify failing service and blast radius.
2. Quarantine problematic jobs from queue.
3. Scale workers down if resource contention occurs.
4. Recover database and queue consistency.
5. Replay jobs from last checkpoint.
6. Publish post-incident summary.

## Capacity Planning

Track:
- average scan duration
- queue wait times
- CPU/RAM saturation windows
- disk usage growth for reports and screenshots

Use these metrics to tune concurrency and VM size.
