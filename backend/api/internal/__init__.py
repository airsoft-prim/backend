from fastapi import APIRouter

from .health import router as health_router

app_router = APIRouter()

app_router.include_router(health_router)

__all__ = ["app_router"]
