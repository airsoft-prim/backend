from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import BaseModel

if TYPE_CHECKING:
    from .public import Game, Team, User


class UserProfile(BaseModel):
    """Профиль пользователя: публичные данные игрока."""

    __tablename__ = "user_profiles"
    __table_args__ = ({"schema": "info"},)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    full_name: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="profile")


class TeamProfile(BaseModel):
    """Профиль команды: публичные данные.

    Создаётся вместе с командой и удаляется вместе с ней.
    """

    __tablename__ = "team_profiles"
    __table_args__ = ({"schema": "info"},)

    team_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    banner_url: Mapped[str | None] = mapped_column(String(500))
    motto: Mapped[str | None] = mapped_column(String(255))

    team: Mapped[Team] = relationship(back_populates="profile")


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
