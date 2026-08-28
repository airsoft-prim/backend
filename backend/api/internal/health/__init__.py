from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Состояние приложения"])
