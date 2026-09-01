from fastapi import APIRouter

from .committees import router as committees_router
from .health import router as health_router
from .teams import router as teams_router

app_router = APIRouter()

app_router.include_router(health_router)
app_router.include_router(committees_router)
app_router.include_router(teams_router)

__all__ = ["app_router"]
