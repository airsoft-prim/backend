from functools import lru_cache

from pydantic import BaseModel

from .app import ApplicationConfiguration
from .database import PostgresConfiguration
from .storage import MinioConfiguration


class Configs(BaseModel):
    """Конфигурация приложения."""

    app: ApplicationConfiguration = ApplicationConfiguration()
    database: PostgresConfiguration = PostgresConfiguration()
    storage: MinioConfiguration = MinioConfiguration()


@lru_cache
def get_app_config() -> Configs:
    """Метод, предоставляющий конфигурацию приложения.

    Returns:
        Configs: Конфигурация приложения.
    """
    return Configs()


config = get_app_config()
