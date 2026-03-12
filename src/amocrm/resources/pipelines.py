from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

from ..models.pipelines import Pipeline, PipelineStatus

if TYPE_CHECKING:
    from ..client import AmoCRM


class PipelinesResource:
    """Ресурс для работы с воронками и статусами AmoCRM.

    Эндпоинт: ``/api/v4/leads/pipelines``.
    """

    def __init__(self, client: AmoCRM) -> None:
        """
        Args:
            client: Экземпляр клиента :class:`~amocrm.client.AmoCRM`.
        """
        self._client = client

    # ------------------------------------------------------------------ #
    # Pipelines                                                            #
    # ------------------------------------------------------------------ #

    def list(self) -> builtins.list[Pipeline]:
        """Получить список всех воронок аккаунта.

        Returns:
            Список объектов :class:`~amocrm.models.pipelines.Pipeline`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request("GET", "/api/v4/leads/pipelines")
        return [
            Pipeline.from_dict(d)
            for d in raw.get("_embedded", {}).get("pipelines", [])
        ]

    def get(self, pipeline_id: int) -> Pipeline:
        """Получить воронку по идентификатору.

        Args:
            pipeline_id: Идентификатор воронки.

        Returns:
            Объект :class:`~amocrm.models.pipelines.Pipeline`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request("GET", f"/api/v4/leads/pipelines/{pipeline_id}")
        return Pipeline.from_dict(raw)

    def create(self, pipelines: builtins.list[Pipeline]) -> builtins.list[Pipeline]:
        """Создать одну или несколько воронок.

        Args:
            pipelines: Список воронок для создания.

        Returns:
            Список созданных воронок с заполненными идентификаторами.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "POST",
            "/api/v4/leads/pipelines",
            json=[p.to_dict() for p in pipelines],
        )
        return [
            Pipeline.from_dict(d)
            for d in raw.get("_embedded", {}).get("pipelines", [])
        ]

    def update(self, pipeline_id: int, data: Pipeline) -> Pipeline:
        """Обновить воронку по идентификатору.

        Args:
            pipeline_id: Идентификатор воронки.
            data: Объект с обновляемыми полями.

        Returns:
            Обновлённый объект :class:`~amocrm.models.pipelines.Pipeline`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "PATCH",
            f"/api/v4/leads/pipelines/{pipeline_id}",
            json=data.to_dict(),
        )
        return Pipeline.from_dict(raw)

    def delete(self, pipeline_id: int) -> None:
        """Удалить воронку по идентификатору.

        Args:
            pipeline_id: Идентификатор воронки.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        self._client._request("DELETE", f"/api/v4/leads/pipelines/{pipeline_id}")

    # ------------------------------------------------------------------ #
    # Statuses                                                             #
    # ------------------------------------------------------------------ #

    def list_statuses(
        self,
        pipeline_id: int,
        *,
        with_descriptions: bool = False,
    ) -> builtins.list[PipelineStatus]:
        """Получить список статусов воронки.

        Args:
            pipeline_id: Идентификатор воронки.
            with_descriptions: Если ``True``, подгружает описания уровней
                зрелости для каждого статуса.

        Returns:
            Список объектов :class:`~amocrm.models.pipelines.PipelineStatus`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        params = {"with": "descriptions"} if with_descriptions else {}
        raw = self._client._request(
            "GET",
            f"/api/v4/leads/pipelines/{pipeline_id}/statuses",
            params=params,
        )
        return [
            PipelineStatus.from_dict(d)
            for d in raw.get("_embedded", {}).get("statuses", [])
        ]

    def get_status(
        self,
        pipeline_id: int,
        status_id: int,
        *,
        with_descriptions: bool = False,
    ) -> PipelineStatus:
        """Получить статус воронки по идентификатору.

        Args:
            pipeline_id: Идентификатор воронки.
            status_id: Идентификатор статуса.
            with_descriptions: Если ``True``, подгружает описания уровней зрелости.

        Returns:
            Объект :class:`~amocrm.models.pipelines.PipelineStatus`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        params = {"with": "descriptions"} if with_descriptions else {}
        raw = self._client._request(
            "GET",
            f"/api/v4/leads/pipelines/{pipeline_id}/statuses/{status_id}",
            params=params,
        )
        return PipelineStatus.from_dict(raw)

    def create_statuses(
        self,
        pipeline_id: int,
        statuses: builtins.list[PipelineStatus],
    ) -> builtins.list[PipelineStatus]:
        """Создать статусы в воронке.

        Args:
            pipeline_id: Идентификатор воронки.
            statuses: Список статусов для создания.

        Returns:
            Список созданных статусов с заполненными идентификаторами.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "POST",
            f"/api/v4/leads/pipelines/{pipeline_id}/statuses",
            json=[s.to_dict() for s in statuses],
        )
        return [
            PipelineStatus.from_dict(d)
            for d in raw.get("_embedded", {}).get("statuses", [])
        ]

    def update_status(
        self,
        pipeline_id: int,
        status_id: int,
        data: PipelineStatus,
    ) -> PipelineStatus:
        """Обновить статус воронки.

        Args:
            pipeline_id: Идентификатор воронки.
            status_id: Идентификатор статуса.
            data: Объект с обновляемыми полями.

        Returns:
            Обновлённый объект :class:`~amocrm.models.pipelines.PipelineStatus`.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        raw = self._client._request(
            "PATCH",
            f"/api/v4/leads/pipelines/{pipeline_id}/statuses/{status_id}",
            json=data.to_dict(),
        )
        return PipelineStatus.from_dict(raw)

    def delete_status(self, pipeline_id: int, status_id: int) -> None:
        """Удалить статус воронки.

        Args:
            pipeline_id: Идентификатор воронки.
            status_id: Идентификатор статуса.

        Raises:
            AmoCRMAPIError: При ошибке API (статус не 2xx).
        """
        self._client._request(
            "DELETE",
            f"/api/v4/leads/pipelines/{pipeline_id}/statuses/{status_id}",
        )
