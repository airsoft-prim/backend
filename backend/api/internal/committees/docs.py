from fastapi import status

from backend.general.types import RouteDocs

SEARCH_COMMITTEES_DOCS: RouteDocs = {
    "summary": "Поиск орг-комитетов.",
    "operation_id": "searchCommittees",
    "description": (
        "Ищет орг-комитеты по заданным фильтрам с сортировкой и пагинацией. "
        "Поддерживает фильтрацию по названию и датам, сортировку по названию "
        "и датам создания/обновления. Возвращает страницу результатов."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

CREATE_COMMITTEE_DOCS: RouteDocs = {
    "summary": "Создание орг-комитета.",
    "operation_id": "createCommittee",
    "description": (
        "Создаёт новый орг-комитет вместе с его профилем: профиль неразделим "
        "с орг-комитетом и создаётся в том же действии. Орг-комитеты "
        "занимаются организацией игр. Если орг-комитет с таким названием "
        "уже существует - вернётся ошибка 409."
    ),
    "status_code": status.HTTP_201_CREATED,
    "deprecated": False,
}

GET_COMMITTEE_DOCS: RouteDocs = {
    "summary": "Получение орг-комитета.",
    "operation_id": "getCommittee",
    "description": (
        "Возвращает информацию об орг-комитете вместе с профилем. "
        "Если орг-комитет с указанным идентификатором не найден - "
        "вернётся ошибка 404."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

UPDATE_COMMITTEE_DOCS: RouteDocs = {
    "summary": "Обновление орг-комитета.",
    "operation_id": "updateCommittee",
    "description": (
        "Частично обновляет данные орг-комитета: название и/или поля профиля. "
        "Передавать нужно только изменяемые поля. Если новое название уже "
        "занято другим орг-комитетом - вернётся ошибка 409."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

GET_MEMBERS_DOCS: RouteDocs = {
    "summary": "Список участников орг-комитета.",
    "operation_id": "getCommitteeMembers",
    "description": (
        "Возвращает полный список участников орг-комитета. Участников немного, "
        "поэтому список не пагинируется. Поддерживаются фильтры: поиск по "
        "позывному (q), ранг, тег и признак подтверждённости - привязан ли "
        "участник к аккаунту игрока."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

ADD_MEMBER_DOCS: RouteDocs = {
    "summary": "Добавление участника в орг-комитет.",
    "operation_id": "addCommitteeMember",
    "description": (
        "Добавляет участника в орг-комитет: позывной, необязательные ранг и тег. "
        "Если указан user_id - участник сразу привязан к аккаунту игрока; "
        "иначе создаётся виртуальный боец, который будет привязан к аккаунту "
        "при регистрации игрока с таким же позывным. Если позывной уже занят "
        "в орг-комитете или игрок уже состоит в нём - вернётся ошибка 409."
    ),
    "status_code": status.HTTP_201_CREATED,
    "deprecated": False,
}

GET_MEMBER_DOCS: RouteDocs = {
    "summary": "Получение участника орг-комитета.",
    "operation_id": "getCommitteeMember",
    "description": (
        "Возвращает информацию об участнике орг-комитета: позывной, ранг, тег "
        "и признак подтверждённости. Если участник не найден - "
        "вернётся ошибка 404."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

UPDATE_MEMBER_DOCS: RouteDocs = {
    "summary": "Обновление участника орг-комитета.",
    "operation_id": "updateCommitteeMember",
    "description": (
        "Частично обновляет данные участника: позывной, ранг, тег. "
        "Передавать нужно только изменяемые поля. Если новый позывной уже "
        "занят в орг-комитете - вернётся ошибка 409."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

REMOVE_MEMBER_DOCS: RouteDocs = {
    "summary": "Исключение участника из орг-комитета.",
    "operation_id": "removeCommitteeMember",
    "description": (
        "Исключает участника из орг-комитета. Если участник не найден - вернётся ошибка 404."
    ),
    "status_code": status.HTTP_204_NO_CONTENT,
    "deprecated": False,
}
