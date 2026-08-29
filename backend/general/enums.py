from enum import StrEnum


class SortDirection(StrEnum):
    """Направление сортировки."""

    ASC = "asc"
    DESC = "desc"


class FilterOperator(StrEnum):
    """Оператор для фильтрации по полю."""

    EQUAL = "eq"
    # TODO: Добавить ещё операторов


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
