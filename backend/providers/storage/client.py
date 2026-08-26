from minio import Minio

from backend.core.config import Configs, config


def _create_client(config: Configs) -> Minio:
    """Создание клиента объектного хранилища MinIO.

    Args:
        config (Configs): Конфигурация проекта.

    Returns:
        Minio: Клиент MinIO.
    """
    return Minio(
        endpoint=config.storage.ENDPOINT,
        access_key=config.storage.ACCESS_KEY,
        secret_key=config.storage.SECRET_KEY,
        secure=config.storage.SECURE,
        region=config.storage.REGION,
        cert_check=config.storage.CERT_CHECK,
    )


client = _create_client(config)


async def get_storage() -> Minio:
    """Возвращает клиент подключения к Minio.

    Returns:
        Minio: Клиент хранилища S3 Minio.
    """
    return client
