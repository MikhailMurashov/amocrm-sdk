from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any

_PIPELINE_SCALAR_FIELDS = (
    "id", "name", "sort", "is_main", "is_unsorted_on", "is_archive", "account_id",
)

_STATUS_SCALAR_FIELDS = (
    "id", "name", "sort", "is_editable", "pipeline_id", "color", "type", "account_id",
)


@dataclass(kw_only=True)
class StatusDescription:
    id: int | None = None
    level: str | None = None  # newbie / candidate / master
    text: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StatusDescription:
        return cls(
            id=data.get("id"),
            level=data.get("level"),
            text=data.get("text"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass(kw_only=True)
class PipelineStatus:
    id: int | None = None
    name: str | None = None
    sort: int | None = None
    is_editable: bool | None = None
    pipeline_id: int | None = None
    color: str | None = None
    type: int | None = None
    account_id: int | None = None
    descriptions: list[StatusDescription] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PipelineStatus:
        descriptions_raw = data.get("descriptions")
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            sort=data.get("sort"),
            is_editable=data.get("is_editable"),
            pipeline_id=data.get("pipeline_id"),
            color=data.get("color"),
            type=data.get("type"),
            account_id=data.get("account_id"),
            descriptions=(
                [StatusDescription.from_dict(d) for d in descriptions_raw]
                if descriptions_raw is not None else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            k: getattr(self, k)
            for k in _STATUS_SCALAR_FIELDS
            if getattr(self, k) is not None
        }
        if self.descriptions is not None:
            result["descriptions"] = [d.to_dict() for d in self.descriptions]
        return result


@dataclass(kw_only=True)
class Pipeline:
    id: int | None = None
    name: str | None = None
    sort: int | None = None
    is_main: bool | None = None
    is_unsorted_on: bool | None = None
    is_archive: bool | None = None
    account_id: int | None = None
    statuses: list[PipelineStatus] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Pipeline:
        statuses_raw = data.get("_embedded", {}).get("statuses")
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            sort=data.get("sort"),
            is_main=data.get("is_main"),
            is_unsorted_on=data.get("is_unsorted_on"),
            is_archive=data.get("is_archive"),
            account_id=data.get("account_id"),
            statuses=(
                [PipelineStatus.from_dict(s) for s in statuses_raw.values()]
                if isinstance(statuses_raw, dict)
                else [PipelineStatus.from_dict(s) for s in statuses_raw]
                if statuses_raw is not None else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            k: getattr(self, k)
            for k in _PIPELINE_SCALAR_FIELDS
            if getattr(self, k) is not None
        }
        if self.statuses is not None:
            result["_embedded"] = {
                "statuses": [s.to_dict() for s in self.statuses]
            }
        return result
