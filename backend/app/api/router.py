from fastapi import APIRouter

from app.api.routes import clusters, events, health, logs, nodes, pods
from app.core.config import get_settings

settings = get_settings()

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(clusters.router, prefix=settings.api_prefix, tags=["clusters"])
api_router.include_router(nodes.router, prefix=settings.api_prefix, tags=["nodes"])
api_router.include_router(pods.router, prefix=settings.api_prefix, tags=["pods"])
api_router.include_router(events.router, prefix=settings.api_prefix, tags=["events"])
api_router.include_router(logs.router, prefix=settings.api_prefix, tags=["logs"])
