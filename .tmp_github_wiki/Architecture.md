# Architecture

## Service Topology

Expl0V1N uses a microservices architecture with clear separation of concerns:

- Frontend (React)
- Backend API (FastAPI)
- Orchestrator (Celery workers)
- Redis (queue and broker)
- PostgreSQL (state and reports)
- Scanner tool containers
- AI assistant service
- Notification service
- Nginx gateway

## Data Flow

1. User creates scan or pipeline from UI.
2. Backend validates auth, scope, and parameters.
3. Backend writes job metadata to PostgreSQL.
4. Backend enqueues task into Redis/Celery queue.
5. Orchestrator executes tools in policy-defined sequence.
6. Results are normalized and persisted.
7. UI receives status/progress updates.
8. Reports exported as PDF and JSON.

## Queue Model

- Queue names: vapt, hunting, default
- VAPT: one active target by policy
- Hunting: one active pipeline by default
- Retries with backoff and checkpointing

## Network Model

- frontend-net: UI and gateway traffic
- backend-net: API and data services
- scan-net: scanner execution plane

Scanner services do not require direct exposure to public internet beyond controlled outbound resolution/probing.
