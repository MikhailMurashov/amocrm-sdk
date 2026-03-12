class AmoCRMError(Exception):
    """Базовый класс исключений SDK."""


class AmoCRMAPIError(AmoCRMError):
    """Исключение при ошибке API AmoCRM (статус не 2xx).

    Attributes:
        status_code: HTTP-статус ответа.
        body: Тело ответа в виде строки.
    """

    def __init__(self, status_code: int, body: str) -> None:
        """
        Args:
            status_code: HTTP-статус ответа API.
            body: Тело ответа API в виде строки.
        """
        self.status_code = status_code
        self.body = body
        super().__init__(f"AmoCRM API error {status_code}: {body}")


class AmoCRMTokenRefreshError(AmoCRMError):
    """Исключение при неудачном обновлении токена доступа."""


class AmoCRMNotConfiguredError(AmoCRMError):
    """Исключение при использовании менеджера до его настройки."""
