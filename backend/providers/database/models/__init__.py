from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Единый naming convention: Alembic генерирует миграции,
# имена констрейнтов и индексов в них консистентны.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class BaseModel(AsyncAttrs, DeclarativeBase):
    """Базовый класс всех ORM-моделей.

    AsyncAttrs даёт awaitable_attrs: ленивая загрузка отношений
    в асинхронном коде через `await obj.awaitable_attrs.<relation>`.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class DatedBaseModel(BaseModel):
    """Базовый класс ORM-моделей, для которых
    необходимо отслеживать временные метки.
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


from .info import GameProfile, UnionProfile, UserProfile  # noqa: E402
from .public import Game, GameRegistration, Union, UnionMember, User  # noqa: E402

__all__ = [
    "NAMING_CONVENTION",
    "BaseModel",
    "Game",
    "GameProfile",
    "GameRegistration",
    "Union",
    "UnionMember",
    "UnionProfile",
    "User",
    "UserProfile",
]
