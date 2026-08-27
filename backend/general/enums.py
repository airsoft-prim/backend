from enum import StrEnum


class UserRole(StrEnum):
    """Роль пользователя на портале."""

    PLAYER = "player"
    ADMIN = "admin"


class UnionMemberRank(StrEnum):
    """Ранг участника объединения."""

    MEMBER = "member"
    DEPUTY_COMMANDER = "deputy_commander"
    COMMANDER = "commander"


class UnionType(StrEnum):
    """Тип объединения: команда или оргкомитет."""

    TEAM = "team"
    ORG_COMMITTEE = "org_committee"


class GameStatus(StrEnum):
    """Статус игры: черновик, регистрация, проведение, завершена."""

    DRAFT = "draft"
    REGISTRATION = "registration"
    ONGOING = "ongoing"
    COMPLETED = "completed"


class GameTag(StrEnum):
    """Тег игры — формат или жанр: CQB, тренировка, воскреска, милсим,
    ролевая игра, сценарная игра, штурм, оборона, захват флага,
    ночная игра, зомби-апокалипсис."""

    CQB = "cqb"
    TRAINING = "training"
    RESPAWN = "respawn"
    MILSIM = "milsim"
    ROLEPLAY = "roleplay"
    SCENARIO = "scenario"
    ASSAULT = "assault"
    DEFENSE = "defense"
    CAPTURE_THE_FLAG = "capture_the_flag"
    NIGHT = "night"
    ZOMBIE = "zombie"
