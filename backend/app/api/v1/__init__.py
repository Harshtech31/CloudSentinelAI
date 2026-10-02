"""
API v1 Package: aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import auth, dashboard, findings, graph, health, reports, scan

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(scan.router)
api_router.include_router(findings.router)
api_router.include_router(graph.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)

__all__ = ["api_router"]
