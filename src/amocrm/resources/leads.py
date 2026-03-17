from __future__ import annotations

import builtins
from typing import Any

from ..exceptions import AmoCRMError
from ..models.leads import ComplexLeadResult, Lead
from ._base import BaseResource


class LeadsResource(BaseResource[Lead]):
    """Ресурс для работы со сделками AmoCRM (``/api/v4/leads``)."""

    _path = "/api/v4/leads"
    _embedded_key = "leads"
    _dto_class = Lead

    def get(
        self,
        lead_id: int,
        *,
        with_: builtins.list[str] | None = None,
    ) -> Lead:
        """Получить сделку по идентификатору.

        По умолчанию подгружает связанные контакты (``contacts``). Чтобы
        отключить это поведение или запросить другой набор данных, передайте
        ``with_`` явно, например ``with_=[]`` или
        ``with_=["contacts", "companies"]``.

        Args:
            lead_id: Идентификатор сделки.
            with_: Список дополнительных данных для подгрузки.
                По умолчанию ``["contacts"]``.

        Returns:
            Объект :class:`~amocrm.models.leads.Lead`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        if with_ is None:
            with_ = ["contacts"]
        return super().get(lead_id, with_=with_)

    def create_complex(
        self, leads: builtins.list[Lead]
    ) -> builtins.list[ComplexLeadResult]:
        """Сложное создание сделок со связанными сущностями.

        Использует эндпоинт ``POST /api/v4/leads/complex``, позволяющий
        одновременно создавать сделки вместе с контактами и компаниями.

        Args:
            leads: Список сделок для создания.

        Returns:
            Список результатов создания с идентификаторами сделок и связанных
            сущностей.

        Raises:
            AmoCRMError: Если передано более 50 сделок или у сделки
                более одного контакта.
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        if len(leads) > self._max_per_request:
            raise AmoCRMError(
                f"create_complex allows at most {self._max_per_request} leads"
                " per request"
            )
        for lead in leads:
            if lead.contacts is not None and len(lead.contacts) > 1:
                raise AmoCRMError("create_complex allows at most 1 contact per lead")
        raw: list[dict[str, Any]] = self._client._request(  # type: ignore[assignment]
            "POST", "/api/v4/leads/complex", json=[lead.to_dict() for lead in leads]
        )
        return [ComplexLeadResult.from_dict(d) for d in raw]
