from enum import StrEnum


class UserRole(StrEnum):
    """Роль пользователя на портале."""

    PLAYER = "player"
    ADMIN = "admin"


class TeamMemberRank(StrEnum):
    """Ранг участника команды."""

    MEMBER = "member"
    DEPUTY_COMMANDER = "deputy_commander"
    COMMANDER = "commander"
