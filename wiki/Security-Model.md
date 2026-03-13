# Security Model

## Access Control

- All scan operations require authentication.
- Role model: admin and user.
- Admin controls user management and approvals.
- User operations are scope-restricted.

## Scope Enforcement

- Targets must pass format validation.
- External targets require approval.
- Domain/IP allowlisting is enforced server-side.

## Runtime Safety

- No automatic exploitation
- Resource guard checks before execution
- Queue throttling and policy-based sequencing
- Tool-level timeouts and rate limits

## Auditability

- Every sensitive action is logged:
  - who
  - what
  - when
  - from where
- Logs include scan create/start/cancel/export and settings updates.

## Secrets Management

- Use .env for local development only.
- Use secret manager in production.
- Rotate keys and tokens regularly.
