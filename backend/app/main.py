"""Expl0V1N Backend — FastAPI Application Entry Point."""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.api import router as api_router
from app.core.middleware import AuditLogMiddleware, RateLimitMiddleware
from app.core.startup import create_default_admin
from app.models import user, scan, hunting  # noqa: F401

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Starting Expl0V1N Backend", env=settings.app_env)

    # Create tables (use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create default admin user
    await create_default_admin()

    logger.info("Expl0V1N Backend started successfully")
    yield

    # Shutdown
    await engine.dispose()
    logger.info("Expl0V1N Backend shut down")


app = FastAPI(
    title="Expl0V1N API",
    description="Vulnerability Assessment, Penetration Testing & Bug Hunting Platform",
    version="1.0.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[h.strip() for h in settings.allowed_hosts.split(",")],
)

app.add_middleware(AuditLogMiddleware)
app.add_middleware(RateLimitMiddleware)

# ── Routes ───────────────────────────────────────────────────

app.include_router(api_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "expl0v1n-backend"}
