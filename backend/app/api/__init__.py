"""API Router — aggregates all endpoint routers."""

from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.scans import router as scans_router
from app.api.hunting import router as hunting_router
from app.api.reports import router as reports_router
from app.api.notifications import router as notifications_router
from app.api.ai_chat import router as ai_router
from app.api.dashboard import router as dashboard_router
from app.api.ws import router as ws_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(scans_router, prefix="/scans", tags=["VAPT Scans"])
router.include_router(hunting_router, prefix="/hunting", tags=["Bug Hunting"])
router.include_router(reports_router, prefix="/reports", tags=["Reports"])
router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
router.include_router(ai_router, prefix="/ai", tags=["AI Assistant"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(ws_router, prefix="/ws", tags=["Realtime"])
