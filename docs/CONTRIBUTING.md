# Contributing

## Development Setup

1. Fork + clone repository.
2. Copy `.env.example` to `.env`.
3. Start stack with desired profiles.
4. Run tests/lint before committing.

## Code Style

- Python: Black + Ruff + type hints for public functions.
- Frontend: TypeScript strict mode + ESLint.
- Keep modules cohesive and testable.

## Branch Naming

- `feat/<short-description>`
- `fix/<short-description>`
- `docs/<short-description>`
- `chore/<short-description>`

## Pull Request Template

Include:
- What changed
- Why it changed
- Security impact
- Test evidence
- Screenshots (if UI changed)

## Issue Templates

- Bug Report: repro steps, expected vs actual, logs
- Feature Request: problem, proposal, acceptance criteria

## Testing Guidelines

- Unit tests for validators, parsers, normalizers.
- Integration tests for API endpoints and orchestration paths.
- Security regression tests for auth, scope, and safe defaults.

## Responsible Use

Contributors must not add offensive capabilities or unsafe defaults. Defensive and authorized-use only.
