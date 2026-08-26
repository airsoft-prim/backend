from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import BaseModel

if TYPE_CHECKING:
    from .auth import User


class UserProfile(BaseModel):
    """Профиль пользователя: публичные данные игрока.

    Отдельная запись от учётной записи — профиль может отсутствовать,
    пока пользователь его не заполнил.
    """

    __tablename__ = "user_profiles"
    __table_args__ = ({"schema": "profile"},)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth.users.id", ondelete="CASCADE"), primary_key=True
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    full_name: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="profile")
