from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.custom_fields import CustomFieldDefinition

if TYPE_CHECKING:
    from ..client import AmoCRM


class CustomFieldsResource:
    """Ресурс для работы с кастомными полями AmoCRM.

    Эндпоинт: ``/api/v4/{entity}/custom_fields``.
    """

    def __init__(self, client: AmoCRM) -> None:
        """
        Args:
            client: Экземпляр клиента :class:`~amocrm.client.AmoCRM`.
        """
        self._client = client

    def list(self, entity: str) -> list[CustomFieldDefinition]:
        """Получить список кастомных полей для сущности.

        Args:
            entity: Тип сущности: ``"leads"``, ``"contacts"`` или ``"companies"``.

        Returns:
            Список объектов :class:`~amocrm.models.custom_fields.CustomFieldDefinition`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request("GET", f"/api/v4/{entity}/custom_fields")
        return [
            CustomFieldDefinition.from_dict(d)
            for d in raw.get("_embedded", {}).get("custom_fields", [])
        ]

    def get(self, entity: str, field_id: int) -> CustomFieldDefinition:
        """Получить кастомное поле по идентификатору.

        Args:
            entity: Тип сущности: ``"leads"``, ``"contacts"`` или ``"companies"``.
            field_id: Идентификатор кастомного поля.

        Returns:
            Объект :class:`~amocrm.models.custom_fields.CustomFieldDefinition`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request("GET", f"/api/v4/{entity}/custom_fields/{field_id}")
        return CustomFieldDefinition.from_dict(raw)
