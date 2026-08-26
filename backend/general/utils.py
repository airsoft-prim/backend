from enum import Enum


def enum_values(enum_cls: type[Enum]) -> list[str]:
    """Значения enum для хранения в БД: member.value вместо member.name.

    Передаётся в sa.Enum как values_callable.
    """
    return [member.value for member in enum_cls]
