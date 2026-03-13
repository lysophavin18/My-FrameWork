from __future__ import annotations

import time
import uuid

import orjson
import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.routers import ai, auth, health, hunting, scans, settings, targets, users
from app.core.config import get_settings
from app.core.rate_limit import RateLimitMiddleware
from app.core.startup import ensure_default_admin
from app.core.telemetry import RequestIdMiddleware
from app.db.session import SessionLocal
from app.services.audit import write_audit_log


def create_app() -> FastAPI:
    settings_obj = get_settings()
    app = FastAPI(
        title="Expl0V1N API",
        version="0.1.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    allow_origins = [o.strip() for o in settings_obj.cors_allow_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(RateLimitMiddleware)

    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(targets.router, prefix="/api/v1/targets", tags=["targets"])
    app.include_router(scans.router, prefix="/api/v1/scans", tags=["scans"])
    app.include_router(hunting.router, prefix="/api/v1/hunting", tags=["hunting"])
    app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
    app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])

    @app.on_event("startup")
    async def _startup():
        app.state.redis = redis.from_url(settings_obj.redis_url, encoding="utf-8", decode_responses=True)
        ensure_default_admin()

    @app.on_event("shutdown")
    async def _shutdown():
        redis_client = getattr(app.state, "redis", None)
        if redis_client is not None:
            await redis_client.close()

    @app.middleware("http")
    async def _audit(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)

        request_id = request.state.request_id
        user_id = getattr(request.state, "user_id", None)
        ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or request.client.host
        user_agent = request.headers.get("user-agent")

        db = SessionLocal()
        try:
            write_audit_log(
                db=db,
                request_id=request_id,
                user_id=user_id,
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                ip=ip,
                user_agent=user_agent,
                duration_ms=duration_ms,
            )
            db.commit()
        finally:
            db.close()

        response.headers["x-request-id"] = request_id
        return response

    @app.exception_handler(ValueError)
    async def _value_error_handler(_request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    return app


app = create_app()

