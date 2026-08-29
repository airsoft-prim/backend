from collections.abc import Callable
from enum import StrEnum
import operator
from typing import Any


class SortDirection(StrEnum):
    """Направление сортировки."""

    ASC = "asc"
    DESC = "desc"


class FilterOperator(StrEnum):
    """Оператор для фильтрации по полю."""

    EQUAL = "eq"
    NOT_EQUAL = "ne"
    LESS_THAN = "lt"
    LESS_OR_EQUAL = "le"
    GREATER_THAN = "gt"
    GREATER_OR_EQUAL = "ge"

    @property
    def python(self) -> Callable[[Any, Any], Any]:
        """Возвращет соответствующий Python-оператор."""
        return {
            self.EQUAL: operator.eq,
            self.NOT_EQUAL: operator.ne,
            self.LESS_THAN: operator.lt,
            self.LESS_OR_EQUAL: operator.le,
            self.GREATER_THAN: operator.gt,
            self.GREATER_OR_EQUAL: operator.ge,
        }[self]


class UserRole(StrEnum):
    """Роль пользователя на портале."""

    PLAYER = "player"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UnionMemberRank(StrEnum):
    """Ранг участника объединения."""

    MEMBER = "member"
    DEPUTY_COMMANDER = "deputy_commander"
    COMMANDER = "commander"


class UnionType(StrEnum):
    """Тип объединения."""

    TEAM = "team"
    COMMITTEE = "committee"


class UnionRecruitmentStatus(StrEnum):
    """Статус набора в объединение."""

    OPEN = "open"
    CLOSED = "closed"


class UnionStatus(StrEnum):
    """Статус объединения."""

    ANNOUNCED = "announced"
    CONFIRMED = "confirmed"


class GameStatus(StrEnum):
    """Статус игры, означающий этап проведения."""

    DRAFT = "draft"
    REGISTRATION = "registration"
    ONGOING = "ongoing"
    COMPLETED = "completed"


class GameTag(StrEnum):
    """Тег игры, означающий формат или жанр."""

    CQB = "cqb"
    TRAINING = "training"
    SUNDAY = "sunday"
    MILSIM = "milsim"
    ROLEPLAY = "roleplay"
    SCENARIO = "scenario"
    ASSAULT = "assault"
    DEFENSE = "defense"
    CAPTURE_THE_FLAG = "capture_the_flag"
    NIGHT = "night"
    ZOMBIE = "zombie"
    MULTIDAY = "multiday"
