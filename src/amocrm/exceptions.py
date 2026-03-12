class AmoCRMError(Exception):
    """Base SDK exception."""


class AmoCRMAPIError(AmoCRMError):
    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"AmoCRM API error {status_code}: {body}")
