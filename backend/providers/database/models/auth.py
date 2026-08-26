from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Column, Enum, ForeignKey, Identity, String, Table, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.general.enums import UserRole
from backend.general.utils import enum_values

from . import BaseModel, DatedBaseModel

if TYPE_CHECKING:
    from .profile import UserProfile


class User(DatedBaseModel):
    """Игрок, зарегистрированный на портале."""

    __tablename__ = "users"
    __table_args__ = ({"schema": "auth"},)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    callsign: Mapped[str] = mapped_column(String(50), unique=True)

    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    profile: Mapped[UserProfile | None] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    roles: Mapped[list[Role]] = relationship(
        secondary="auth.users_roles",
        back_populates="users",
    )


RoleName = Enum(UserRole, name="user_role", values_callable=enum_values)


class Role(BaseModel):
    """Роль пользователя в системе RBAC."""

    __tablename__ = "roles"
    __table_args__ = ({"schema": "auth"},)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[UserRole] = mapped_column(RoleName, unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    users: Mapped[list[User]] = relationship(
        secondary="auth.users_roles",
        back_populates="roles",
    )


user_roles = Table(
    "users_roles",
    BaseModel.metadata,
    Column(
        "user_id",
        BigInteger,
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        BigInteger,
        ForeignKey("auth.roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    schema="auth",
)
