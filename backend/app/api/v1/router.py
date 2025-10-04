"""
Main API Router
Combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    ingestion,
    dashboard,
    pests,
    canopy,
    insights,
    alerts,
    analytics,
    drone
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    ingestion.router,
    prefix="/ingestion",
    tags=["ingestion"]
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"]
)

api_router.include_router(
    pests.router,
    prefix="/pests",
    tags=["pests"]
)

api_router.include_router(
    canopy.router,
    prefix="/canopy",
    tags=["canopy"]
)

api_router.include_router(
    insights.router,
    prefix="/insights",
    tags=["insights"]
)

api_router.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["alerts"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

api_router.include_router(
    drone.router,
    prefix="/drone",
    tags=["drone"]
)
