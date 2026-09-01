from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field
from pydantic.networks import AnyHttpUrl

from backend.general.enums import UnionStatus, UnionType
from backend.general.schemas import SearchBody, SearchParams


class CommitteesFilterFields(StrEnum):
    """Поля для фильтрации по орг-комитетам."""

    NAME = "name"
    CITY = "city"


class CommitteesSortFields(StrEnum):
    """Поля для сортировки орг-комитетов."""

    NAME = "name"
    DATE_CREATE = "date_create"
    MEMBERS = "members"


SearchCommitteesParams = SearchParams
SearchCommitteesBody = SearchBody[CommitteesFilterFields, CommitteesSortFields]


class CommitteeRecord(BaseModel):
    """Запись о найденном орг-комитете."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=0, description="Идентификатор орг-комитета")
    members: int = Field(ge=1, description="Количество участников")
    date_create: datetime = Field(description="Дата создания орг-комитета")
    name: str = Field(description="Название орг-комитета")
    city: str | None = Field(description="Город размещения")
    motto: str | None = Field(description="Девиз орг-комитета")
    status: UnionStatus = Field(description="Статус орг-комитета")
    avatar_url: AnyHttpUrl | None = Field(default=None, description="Ссылка на аватар")


class CreateCommitteeBody(BaseModel):
    """Параметры создания орг-комитета.

    Камуфляж и цвет снаряжения комитету не задаются: они фиксированы
    (`None` и «Светоотражающий» соответственно).
    """

    name: str = Field(description="Название орг-комитета")
    motto: str | None = Field(default=None, description="Девиз орг-комитета")
    city: str | None = Field(default=None, description="Город размещения")
    avatar_url: str | None = Field(default=None, description="Ссылка на аватар")


class CreatedCommittee(BaseModel):
    """Созданный орг-комитет: идентификатор и название."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=0, description="Идентификатор орг-комитета")
    name: str = Field(description="Название орг-комитета")


class Committee(BaseModel):
    """Страница орг-комитета: полные данные.

    Список участников и игры орг-комитета отдаются отдельными запросами.
    У орг-комитета нет камуфляжа (`camo_color` всегда `None`), а цвет
    снаряжения фиксирован — «Светоотражающий». Набор в комитет не ведётся,
    поэтому `recruitment_status` отсутствует.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(ge=0, description="Идентификатор орг-комитета")
    name: str = Field(description="Название орг-комитета")
    type: UnionType = Field(description="Тип объединения")
    status: UnionStatus = Field(description="Статус орг-комитета")
    city: str | None = Field(default=None, description="Город размещения")
    camo_color: str | None = Field(
        default=None, description="Цвет камуфляжа: у орг-комитетов отсутствует"
    )
    gear_color: str = Field(description="Цвет снаряжения: у орг-комитетов — светоотражающий")
    date_create: datetime = Field(description="Дата создания орг-комитета")

    motto: str | None = Field(default=None, description="Девиз орг-комитета")
    description: str | None = Field(default=None, description="Описание орг-комитета")
    avatar_url: AnyHttpUrl | None = Field(default=None, description="Ссылка на аватар")
    banner_url: AnyHttpUrl | None = Field(default=None, description="Ссылка на баннер")

    members: int = Field(ge=0, description="Количество участников")


class UpdateCommitteeBody(BaseModel):
    """Обновляемые данные орг-комитета: передаются только изменяемые поля.

    Камуфляж, цвет снаряжения и состояние набора у комитета фиксированы
    и обновлению не подлежат.
    """

    name: str | None = Field(default=None, description="Название орг-комитета")
    city: str | None = Field(default=None, description="Город размещения")
    motto: str | None = Field(default=None, description="Девиз орг-комитета")
    description: str | None = Field(default=None, description="Описание орг-комитета")
    avatar_url: str | None = Field(default=None, description="Ссылка на аватар")
    banner_url: str | None = Field(default=None, description="Ссылка на баннер")
