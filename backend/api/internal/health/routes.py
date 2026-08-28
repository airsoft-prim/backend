from fastapi import status
from fastapi.responses import PlainTextResponse
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.providers.database import engine

from . import router
from .docs import LIVENESS_DOCS, READINESS_DOCS


@router.get("/liveness", **LIVENESS_DOCS)
async def liveness_healthcheck() -> PlainTextResponse:
    """Функция проверки доступности приложения.

    Returns:
        JSONResponse: Ответ в формате JSON.
    """
    logger.success("Application healthy.")

    return PlainTextResponse(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/readiness", **READINESS_DOCS)
async def readiness_healthcheck() -> PlainTextResponse:
    """Функция проверки готовности приложения.

    Returns:
        JSONResponse: Ответ в формате JSON.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

    except SQLAlchemyError:
        logger.critical("Postgres database is unavailable.")
        return PlainTextResponse(status_code=status.HTTP_503_INTERNAL_SERVER_ERROR)

    logger.success("Application ready.")
    return PlainTextResponse(status_code=status.HTTP_204_NO_CONTENT)
