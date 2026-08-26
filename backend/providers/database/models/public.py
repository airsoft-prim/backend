from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Identity, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import DatedBaseModel

if TYPE_CHECKING:
    from .profile import UserProfile


class User(DatedBaseModel):
    """Игрок, зарегистрированный на портале."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    callsign: Mapped[str] = mapped_column(String(50), unique=True)

    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    profile: Mapped[UserProfile] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
