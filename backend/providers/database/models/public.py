from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.general.enums import (
    GameStatus,
    GameTag,
    UnionMemberRank,
    UnionRecruitmentStatus,
    UnionStatus,
    UnionType,
)
from backend.general.utils import enum_values

from . import DatedBaseModel

if TYPE_CHECKING:
    from .auth import User
    from .info import GameProfile, UnionProfile


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
    recruitment_status: Mapped[UnionRecruitmentStatus] = mapped_column(
        Enum(UnionRecruitmentStatus, name="union_recruitment_status", values_callable=enum_values),
        default=UnionRecruitmentStatus.OPEN,
        server_default=UnionRecruitmentStatus.OPEN.value,
    )
    status: Mapped[UnionStatus] = mapped_column(
        Enum(UnionStatus, name="union_status", values_callable=enum_values),
        default=UnionStatus.ANNOUNCED,
        server_default=UnionStatus.ANNOUNCED.value,
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
    """Отображение учётной записи игрока (User) на страйкбольный домен.

    Связывает игрока со страйкбольными сущностями — объединениями и играми.
    Запись может быть «виртуальным бойцом» — без привязки к учётной записи
    (user_id = NULL): командир вписывает бойца без регистрации на портале.
    Такой участник считается неподтверждённым, но вполне считается за живого.
    """

    __tablename__ = "union_members"
    __table_args__ = (
        UniqueConstraint("union_id", "user_id", name="uq_union_members_union_id_user_id"),
        UniqueConstraint("union_id", "callsign", name="uq_union_members_union_id_callsign"),
        Index(None, "user_id", postgresql_using="hash"),
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
        BigInteger, ForeignKey("auth.users.id", ondelete="SET NULL")
    )

    union: Mapped[Union] = relationship(back_populates="members")
    user: Mapped[User | None] = relationship(back_populates="memberships")
    registrations: Mapped[list[GameRegistration]] = relationship(
        back_populates="member",
        cascade="all, delete-orphan",
    )

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
    __table_args__ = (
        CheckConstraint("end_at > start_at", name="end_after_start"),
        CheckConstraint("check_in_at <= start_at", name="checkin_before_start"),
        CheckConstraint("entry_fee >= 0", name="entry_fee_non_negative"),
        CheckConstraint("max_players IS NULL OR max_players > 0", name="max_players_positive"),
        Index(None, "organizer_id", postgresql_using="hash"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus, name="game_status", values_callable=enum_values),
        default=GameStatus.DRAFT,
        server_default=GameStatus.DRAFT.value,
    )
    tags: Mapped[list[GameTag]] = mapped_column(
        ARRAY(Enum(GameTag, name="game_tag", values_callable=enum_values)),
        default=list,
        server_default="{}",
    )

    max_players: Mapped[int | None] = mapped_column(Integer)
    entry_fee: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    location_name: Mapped[str] = mapped_column(String(200))
    location_url: Mapped[str | None] = mapped_column(String(500))

    check_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    organizer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("unions.id", ondelete="RESTRICT")
    )

    profile: Mapped[GameProfile | None] = relationship(
        back_populates="game",
        uselist=False,
        cascade="all, delete-orphan",
    )
    organizer: Mapped[Union] = relationship(back_populates="organized_games")
    registrations: Mapped[list[GameRegistration]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
    )


class GameRegistration(DatedBaseModel):
    """Регистрация участника объединения на игру.

    Регистрация ссылается на участника объединения (UnionMember), а не на
    учётную запись: команда может записать на игру и «виртуального» бойца
    без регистрации на портале. Ограничения бизнес-процесса (кто и как
    регистрируется) — уровень сервисного слоя, не БД.
    """

    __tablename__ = "game_registrations"
    __table_args__ = (
        Index(None, "game_id", postgresql_using="hash"),
        Index(None, "member_id", postgresql_using="hash"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    game_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("games.id", ondelete="CASCADE"))
    member_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("union_members.id", ondelete="CASCADE")
    )

    game: Mapped[Game] = relationship(back_populates="registrations")
    member: Mapped[UnionMember] = relationship(back_populates="registrations")
