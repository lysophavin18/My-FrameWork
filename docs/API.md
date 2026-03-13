# API Reference

Base URL: `http://localhost:8000/api/v1`
Auth: Bearer JWT (`Authorization: Bearer <token>`)

## Authentication

- `POST /auth/login`
- `POST /auth/refresh`

### Login Request
```json
{ "email": "admin@expl0v1n.local", "password": "ChangeMeOnFirstLogin!" }
```

### Login Response
```json
{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
```

## Dashboard

- `GET /dashboard/stats`

## VAPT Endpoints

- `POST /scans` create single-target scan
- `GET /scans` list scans
- `GET /scans/{scan_id}` get scan status
- `GET /scans/{scan_id}/findings` list findings
- `POST /scans/{scan_id}/cancel` cancel running scan
- `POST /scans/{scan_id}/approve` approve external target (admin)
- `POST /scans/{scan_id}/deny` deny external target (admin)

## Bug Hunting Endpoints

- `POST /hunting/sessions` start pipeline
- `GET /hunting/sessions`
- `GET /hunting/sessions/{session_id}`
- `GET /hunting/sessions/{session_id}/subdomains`
- `GET /hunting/sessions/{session_id}/live-hosts`
- `GET /hunting/sessions/{session_id}/screenshots`
- `GET /hunting/sessions/{session_id}/findings`
- `POST /hunting/sessions/{session_id}/cancel`
- `POST /hunting/sessions/{session_id}/approve` (admin)
- `POST /hunting/sessions/{session_id}/deny` (admin)

## User Management

- `GET /users/me`
- `GET /users` (admin)
- `POST /users` (admin)
- `PUT /users/{user_id}` (admin)
- `DELETE /users/{user_id}` (admin)

## Reports

- `GET /reports/vapt/{scan_id}/pdf`
- `GET /reports/vapt/{scan_id}/json`
- `GET /reports/hunting/{session_id}/pdf`
- `GET /reports/hunting/{session_id}/json`

## Notifications

- `GET /notifications/config`
- `PUT /notifications/config`
- `POST /notifications/test`

## AI Assistant

- `POST /ai/chat`
- `GET /ai/chat/history`

### AI Chat Request
```json
{
  "message": "Which findings should I prioritize first?",
  "scan_id": 42,
  "action": "prioritize"
}
```

### AI Chat Response
```json
{ "message": "1) Fix critical unauthenticated RCE ..." }
```

## Error Model

```json
{ "detail": "Error description" }
```

Status codes: `200,201,204,400,401,403,404,409,422,429,500`
