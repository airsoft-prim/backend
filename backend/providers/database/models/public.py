from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    String,
    UniqueConstraint,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.general.enums import UnionMemberRank, UnionType
from backend.general.utils import enum_values

from . import DatedBaseModel

if TYPE_CHECKING:
    from .info import GameProfile, UnionProfile, UserProfile


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
    memberships: Mapped[list[UnionMember]] = relationship(back_populates="user")


class Union(DatedBaseModel):
    """Объединение страйкбольного портала: команда или оргкомитет."""

    __tablename__ = "unions"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    type: Mapped[UnionType] = mapped_column(
        Enum(UnionType, name="union_type", values_callable=enum_values),
        default=UnionType.TEAM,
        server_default=UnionType.TEAM.value,
    )

    profile: Mapped[UnionProfile] = relationship(
        back_populates="union",
        uselist=False,
        cascade="all, delete-orphan",
    )
    members: Mapped[list[UnionMember]] = relationship(
        back_populates="union",
        cascade="all, delete-orphan",
    )
    organized_games: Mapped[list[Game]] = relationship(back_populates="organizer")


class UnionMember(DatedBaseModel):
    """Участник объединения.

    Запись может быть «виртуальным бойцом» — без привязки к учётной записи
    (user_id = NULL): командир вписывает бойца без регистрации на портале.
    Такой участник считается неподтверждённым, но вполне считается за живого.
    """

    __tablename__ = "union_members"
    __table_args__ = (
        UniqueConstraint("union_id", "user_id", name="uq_union_members_union_id_user_id"),
        UniqueConstraint("union_id", "callsign", name="uq_union_members_union_id_callsign"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    union_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("unions.id", ondelete="CASCADE"))
    callsign: Mapped[str] = mapped_column(String(50))
    tag: Mapped[str | None] = mapped_column(String(50))
    rank: Mapped[UnionMemberRank] = mapped_column(
        Enum(UnionMemberRank, name="union_member_rank", values_callable=enum_values),
        default=UnionMemberRank.MEMBER,
        server_default=UnionMemberRank.MEMBER.value,
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL")
    )

    union: Mapped[Union] = relationship(back_populates="members")
    user: Mapped[User | None] = relationship(back_populates="memberships")

    @property
    def is_confirmed(self) -> bool:
        """Подтверждён ли участник: привязан ли он к учётной записи.

        Боец, вписанный командиром без регистрации, остаётся
        неподтверждённым, пока не свяжет свой аккаунт.
        """
        return self.user is not None


class Game(DatedBaseModel):
    """Игра (мероприятие) страйкбольного портала."""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    organizer_union_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("unions.id", ondelete="RESTRICT")
    )

    max_players: Mapped[int | None] = mapped_column(Integer)
    entry_fee: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    location_name: Mapped[str] = mapped_column(String(200))
    location_url: Mapped[str | None] = mapped_column(String(500))

    check_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    profile: Mapped[GameProfile | None] = relationship(
        back_populates="game",
        uselist=False,
        cascade="all, delete-orphan",
    )
    organizer: Mapped[Union] = relationship(back_populates="organized_games")
