from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI
from loguru import logger

from backend.api import app_router
from backend.core.config import config

APP_DESCRIPTION: Final[str] = """
Серверная часть Страйкбольного портала в Приморском Крае.
"""


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Lifespan приложения FastAPI."""

    logger.info("Application starting up...")
    logger.info(f"Debug mode is {'OOFNF'[config.app.DEBUG :: 2]}.")

    yield

    logger.warning("Application is shutting down.")


app = FastAPI(
    title=config.app.NAME,
    description=APP_DESCRIPTION,
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(app_router)
