from fastapi import status

from backend.general.types import RouteDocs

SEARCH_TEAMS_DOCS: RouteDocs = {
    "summary": "Поиск команд.",
    "operation_id": "searchTeams",
    "description": (
        "Ищет команды по заданным фильтрам с сортировкой и пагинацией. "
        "Поддерживает фильтрацию по названию и датам, сортировку по названию "
        "и датам создания/обновления. Возвращает страницу результатов."
    ),
    "status_code": status.HTTP_200_OK,
    "response_description": "Страница команд.",
    "responses": {
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Некорректные параметры запроса.",
        },
    },
    "deprecated": False,
}

CREATE_TEAM_DOCS: RouteDocs = {
    "summary": "Создание команды.",
    "operation_id": "createTeam",
    "description": (
        "Создаёт новую команду вместе с её профилем: профиль неразделим "
        "с командой и создаётся в том же действии."
    ),
    "status_code": status.HTTP_201_CREATED,
    "response_description": "Созданная команда: идентификатор и название.",
    "responses": {
        status.HTTP_404_NOT_FOUND: {
            "description": "Создающий пользователь не найден.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Некорректное тело запроса.",
        },
    },
    "deprecated": False,
}

GET_TEAM_DOCS: RouteDocs = {
    "summary": "Получение команды.",
    "operation_id": "getTeam",
    "description": "Возвращает информацию о команде вместе с профилем.",
    "status_code": status.HTTP_200_OK,
    "response_description": "Полные данные о команде.",
    "responses": {
        status.HTTP_404_NOT_FOUND: {
            "description": "Команда с указанным идентификатором не найдена."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Некорректный идентификатор команды."
        },
    },
    "deprecated": False,
}

UPDATE_TEAM_DOCS: RouteDocs = {
    "summary": "Обновление команды.",
    "operation_id": "updateTeam",
    "description": (
        "Частично обновляет данные команды: название и/или поля профиля. "
        "Передавать нужно только изменяемые поля."
    ),
    "status_code": status.HTTP_200_OK,
    "response_description": "Обновлённые данные команды.",
    "responses": {
        status.HTTP_404_NOT_FOUND: {
            "description": "Команда с указанным идентификатором не найдена."
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Некорректное тело запроса или идентификатор.",
        },
    },
    "deprecated": False,
}

GET_MEMBERS_DOCS: RouteDocs = {
    "summary": "Список участников команды.",
    "operation_id": "getTeamMembers",
    "description": (
        "Возвращает полный список участников команды. Членов команды немного, "
        "поэтому список не пагинируется. Поддерживаются фильтры: поиск по "
        "позывному (q), ранг, тег и признак подтверждённости - привязан ли "
        "участник к аккаунту игрока."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

ADD_MEMBER_DOCS: RouteDocs = {
    "summary": "Добавление участника в команду.",
    "operation_id": "addTeamMember",
    "description": (
        "Добавляет участника в команду: позывной, необязательные ранг и тег. "
        "Если указан user_id - участник сразу привязан к аккаунту игрока; "
        "иначе создаётся виртуальный боец, который будет привязан к аккаунту "
        "при регистрации игрока с таким же позывным. Если позывной уже занят "
        "в команде или игрок уже состоит в ней - вернётся ошибка 409."
    ),
    "status_code": status.HTTP_201_CREATED,
    "deprecated": False,
}

GET_MEMBER_DOCS: RouteDocs = {
    "summary": "Получение участника команды.",
    "operation_id": "getTeamMember",
    "description": (
        "Возвращает информацию об участнике команды: позывной, ранг, тег "
        "и признак подтверждённости. Если участник не найден - "
        "вернётся ошибка 404."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

UPDATE_MEMBER_DOCS: RouteDocs = {
    "summary": "Обновление участника команды.",
    "operation_id": "updateTeamMember",
    "description": (
        "Частично обновляет данные участника: позывной, ранг, тег. "
        "Передавать нужно только изменяемые поля. Если новый позывной уже "
        "занят в команде - вернётся ошибка 409."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

REMOVE_MEMBER_DOCS: RouteDocs = {
    "summary": "Исключение участника из команды.",
    "operation_id": "removeTeamMember",
    "description": (
        "Исключает участника из команды: его заявки на игры удаляются вместе "
        "с ним. Если участник не найден - вернётся ошибка 404."
    ),
    "status_code": status.HTTP_204_NO_CONTENT,
    "deprecated": False,
}
