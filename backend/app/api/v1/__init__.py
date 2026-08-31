"""
API v1 Router Aggregator for CloudSentinel AI.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.findings import router as findings_router
from app.api.v1.graph import router as graph_router
from app.api.v1.health import router as health_router
from app.api.v1.reports import router as reports_router
from app.api.v1.scan import router as scan_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(scan_router)
api_router.include_router(findings_router)
api_router.include_router(graph_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)

__all__ = ["api_router"]
