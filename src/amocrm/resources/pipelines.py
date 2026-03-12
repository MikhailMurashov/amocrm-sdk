from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

from ..models.pipelines import Pipeline, PipelineStatus

if TYPE_CHECKING:
    from ..client import AmoCRM


class PipelinesResource:
    def __init__(self, client: AmoCRM) -> None:
        self._client = client

    # ------------------------------------------------------------------ #
    # Pipelines                                                            #
    # ------------------------------------------------------------------ #

    def list(self) -> builtins.list[Pipeline]:
        """GET /api/v4/leads/pipelines — список воронок."""
        raw = self._client._request("GET", "/api/v4/leads/pipelines")
        return [
            Pipeline.from_dict(d)
            for d in raw.get("_embedded", {}).get("pipelines", [])
        ]

    def get(self, pipeline_id: int) -> Pipeline:
        """GET /api/v4/leads/pipelines/{id} — получить воронку по ID."""
        raw = self._client._request("GET", f"/api/v4/leads/pipelines/{pipeline_id}")
        return Pipeline.from_dict(raw)

    def create(self, pipelines: builtins.list[Pipeline]) -> builtins.list[Pipeline]:
        """POST /api/v4/leads/pipelines — создать воронки."""
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
        """PATCH /api/v4/leads/pipelines/{id} — обновить воронку."""
        raw = self._client._request(
            "PATCH",
            f"/api/v4/leads/pipelines/{pipeline_id}",
            json=data.to_dict(),
        )
        return Pipeline.from_dict(raw)

    def delete(self, pipeline_id: int) -> None:
        """DELETE /api/v4/leads/pipelines/{id} — удалить воронку."""
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
        """GET /api/v4/leads/pipelines/{pipeline_id}/statuses — список статусов."""
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
        """GET /api/v4/leads/pipelines/{pipeline_id}/statuses/{id} — получить статус."""
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
        """POST /api/v4/leads/pipelines/{pipeline_id}/statuses — создать статусы."""
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
        """PATCH /api/v4/leads/pipelines/{pipeline_id}/statuses/{id} — обновить."""
        raw = self._client._request(
            "PATCH",
            f"/api/v4/leads/pipelines/{pipeline_id}/statuses/{status_id}",
            json=data.to_dict(),
        )
        return PipelineStatus.from_dict(raw)

    def delete_status(self, pipeline_id: int, status_id: int) -> None:
        """DELETE /api/v4/leads/pipelines/{pipeline_id}/statuses/{id} — удалить."""
        self._client._request(
            "DELETE",
            f"/api/v4/leads/pipelines/{pipeline_id}/statuses/{status_id}",
        )
