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
