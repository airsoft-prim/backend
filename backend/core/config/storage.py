from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MinioConfiguration(BaseSettings):
    """Секция конфигурации объектного хранилища MinIO."""

    model_config = SettingsConfigDict(env_prefix="MINIO_")

    ENDPOINT: str = Field(default="localhost:9000")
    ACCESS_KEY: str = Field(default="minioadmin")
    SECRET_KEY: str = Field(default="minioadmin")

    SECURE: bool = Field(default=False)
    REGION: str | None = Field(default=None)
    CERT_CHECK: bool = Field(default=True)
