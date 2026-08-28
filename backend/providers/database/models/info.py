from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import BaseModel

if TYPE_CHECKING:
    from .auth import User
    from .public import Game, Union


class UserProfile(BaseModel):
    """Профиль пользователя: публичные данные игрока."""

    __tablename__ = "user_profiles"
    __table_args__ = ({"schema": "info"},)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth.users.id", ondelete="CASCADE"), primary_key=True
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    full_name: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="profile")


class UnionProfile(BaseModel):
    """Профиль объединения: публичные данные.

    Создаётся вместе с объединением и удаляется вместе с ним.
    """

    __tablename__ = "union_profiles"
    __table_args__ = ({"schema": "info"},)

    union_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("unions.id", ondelete="CASCADE"), primary_key=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    banner_url: Mapped[str | None] = mapped_column(String(500))
    motto: Mapped[str | None] = mapped_column(String(255))

    union: Mapped[Union] = relationship(back_populates="profile")


class GameProfile(BaseModel):
    """Профиль игры: публичные данные.

    Опционален — игра может быть опубликована без профиля.
    """

    __tablename__ = "game_profiles"
    __table_args__ = ({"schema": "info"},)

    game_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    banner_url: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)

    game: Mapped[Game] = relationship(back_populates="profile")
