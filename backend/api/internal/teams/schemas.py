from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field
from pydantic.networks import AnyHttpUrl

from backend.general.enums import (
    UnionMemberRank,
    UnionRecruitmentStatus,
    UnionStatus,
    UnionType,
)
from backend.general.schemas import SearchBody, SearchParams


class TeamsFilterFields(StrEnum):
    """Поля для фильтрации по командам."""

    NAME = "name"
    CITY = "city"
    RECRUITMENT_STATUS = "recruitment_status"


class TeamsSortFields(StrEnum):
    """Поля для сортировки команд."""

    NAME = "name"
    DATE_CREATE = "date_create"
    MEMBERS = "members"


SearchTeamsParams = SearchParams
SearchTeamsBody = SearchBody[TeamsFilterFields, TeamsSortFields]


class TeamRecord(BaseModel):
    """Запись о найденной команде."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=0, description="Идентификатор команды")
    members: int = Field(ge=1, description="Количество участников")
    date_create: datetime = Field(description="Дата создания команды")
    name: str = Field(description="Название команды")
    city: str | None = Field(description="Город размещения")
    motto: str | None = Field(description="Девиз команды")
    status: UnionStatus = Field(description="Статус команды")
    recruitment_status: UnionRecruitmentStatus = Field(description="Состояние набора")
    avatar_url: AnyHttpUrl | None = Field(default=None, description="Ссылка на аватар")


class CreateTeamBody(BaseModel):
    """Параметры создания команды."""

    name: str = Field(description="Название команды")
    motto: str | None = Field(default=None, description="Девиз команды")
    city: str | None = Field(default=None, description="Город размещения")
    avatar_url: str | None = Field(default=None, description="Ссылка на аватар")


class CreatedTeam(BaseModel):
    """Созданная команда: идентификатор и название."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=0, description="Идентификатор команды")
    name: str = Field(description="Название команды")


class Team(BaseModel):
    """Страница команды: полные данные о команде.

    Список участников и игры команды отдаются отдельными запросами.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=0, description="Идентификатор команды")
    name: str = Field(description="Название команды")
    type: UnionType = Field(description="Тип объединения")
    status: UnionStatus = Field(description="Статус команды")
    city: str | None = Field(default=None, description="Город размещения")
    camo_color: str | None = Field(default=None, description="Цвет камуфляжа")
    gear_color: str | None = Field(default=None, description="Цвет снаряжения")
    recruitment_status: UnionRecruitmentStatus = Field(description="Состояние набора")
    date_create: datetime = Field(description="Дата создания команды")

    motto: str | None = Field(default=None, description="Девиз команды")
    description: str | None = Field(default=None, description="Описание команды")
    avatar_url: AnyHttpUrl | None = Field(default=None, description="Ссылка на аватар")
    banner_url: AnyHttpUrl | None = Field(default=None, description="Ссылка на баннер")

    members: int = Field(ge=0, description="Количество участников")


class UpdateTeamBody(BaseModel):
    """Обновляемые данные команды: передаются только изменяемые поля."""

    name: str | None = Field(default=None, description="Название команды")
    city: str | None = Field(default=None, description="Город размещения")
    camo_color: str | None = Field(default=None, description="Цвет камуфляжа")
    gear_color: str | None = Field(default=None, description="Цвет снаряжения")
    motto: str | None = Field(default=None, description="Девиз команды")
    description: str | None = Field(default=None, description="Описание команды")
    avatar_url: str | None = Field(default=None, description="Ссылка на аватар")
    banner_url: str | None = Field(default=None, description="Ссылка на баннер")
    recruitment_status: UnionRecruitmentStatus | None = Field(
        default=None, description="Состояние набора"
    )


class Member(BaseModel):
    """Участник команды."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=0, description="Идентификатор участника")
    callsign: str = Field(description="Позывной участника")
    tag: str | None = Field(default=None, description="Тег участника")
    user_id: int | None = Field(default=None, description="Идентификатор привязанного аккаунта")
    avatar_url: AnyHttpUrl | None = Field(default=None, description="Ссылка на аватар пользователя")


class AddMemberBody(BaseModel):
    """Параметры добавления участника в команду.

    Если в системе уже зарегистрирован игрок с таким позывным — участник
    автоматически привязывается к его аккаунту; иначе остаётся виртуальным
    бойцом до регистрации игрока с таким же позывным.
    """

    callsign: str = Field(description="Позывной участника")


class UpdateMemberBody(BaseModel):
    """Обновляемые данные участника: передаются только изменяемые поля."""

    callsign: str | None = Field(default=None, description="Позывной участника")
    rank: UnionMemberRank | None = Field(default=None, description="Ранг участника")
    tag: str | None = Field(default=None, description="Тег участника")
