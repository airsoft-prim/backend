from fastapi import status

from backend.general.types import RouteDocs

LOGIN_DOCS: RouteDocs = {
    "summary": "Вход в систему.",
    "operation_id": "login",
    "description": (
        "Аутентифицирует игрока по логину и паролю. При успешном входе "
        "возвращает токен доступа (сессию) и данные пользователя. "
        "При неверных учётных данных вернётся ошибка 401."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}

REGISTER_DOCS: RouteDocs = {
    "summary": "Регистрация игрока.",
    "operation_id": "register",
    "description": (
        "Создаёт учётную запись игрока: логин, пароль, позывной. Вместе "
        "с учётной записью создаётся профиль игрока. Если с таким позывным "
        'уже существуют "виртуальные бойцы" в объединениях - они привязываются '
        "к новой учётной записи. Если логин или позывной уже заняты - "
        "вернётся ошибка 409."
    ),
    "status_code": status.HTTP_201_CREATED,
    "deprecated": False,
}

LOGOUT_DOCS: RouteDocs = {
    "summary": "Выход из системы.",
    "operation_id": "logout",
    "description": ("Завершает сессию игрока: токен доступа (сессия) становится недействительным."),
    "status_code": status.HTTP_204_NO_CONTENT,
    "deprecated": False,
}

ME_DOCS: RouteDocs = {
    "summary": "Текущий пользователь.",
    "operation_id": "getMe",
    "description": (
        "Возвращает информацию о текущем аутентифицированном игроке: "
        "позывной, роли, профиль. Если игрок не аутентифицирован - "
        "вернётся ошибка 401."
    ),
    "status_code": status.HTTP_200_OK,
    "deprecated": False,
}
