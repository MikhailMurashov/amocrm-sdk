from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any

_PIPELINE_SCALAR_FIELDS = (
    "id",
    "name",
    "sort",
    "is_main",
    "is_unsorted_on",
    "is_archive",
    "account_id",
)

_STATUS_SCALAR_FIELDS = (
    "id",
    "name",
    "sort",
    "is_editable",
    "pipeline_id",
    "color",
    "type",
    "account_id",
)


@dataclass(kw_only=True)
class StatusDescription:
    """Описание уровня зрелости сделки в статусе воронки.

    Attributes:
        id: Идентификатор описания.
        level: Уровень зрелости (``"newbie"``, ``"candidate"``, ``"master"``).
        text: Текст описания.
    """

    id: int | None = None
    level: str | None = None  # newbie / candidate / master
    text: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StatusDescription:
        """Создать экземпляр из словаря API."""
        return cls(
            id=data.get("id"),
            level=data.get("level"),
            text=data.get("text"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь, исключая поля со значением ``None``."""
        return {k: v for k, v in dataclasses.asdict(self).items() if v is not None}


@dataclass(kw_only=True)
class PipelineStatus:
    """DTO-модель статуса воронки AmoCRM.

    Attributes:
        id: Идентификатор статуса.
        name: Название статуса.
        sort: Порядок сортировки.
        is_editable: Можно ли редактировать статус.
        pipeline_id: Идентификатор воронки, которой принадлежит статус.
        color: HEX-цвет статуса (например, ``"#fffeb2"``).
        type: Тип статуса (0 — обычный, 142 — успешно завершён,
            143 — закрыт и не реализован).
        account_id: Идентификатор аккаунта AmoCRM.
        descriptions: Описания уровней зрелости сделок в этом статусе.
    """

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
        """Создать экземпляр из словаря API."""
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
                if descriptions_raw is not None
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для API, исключая поля со значением ``None``."""
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
    """DTO-модель воронки продаж AmoCRM.

    Attributes:
        id: Идентификатор воронки.
        name: Название воронки.
        sort: Порядок сортировки.
        is_main: Является ли воронка основной.
        is_unsorted_on: Включён ли неразобранный раздел.
        is_archive: Находится ли воронка в архиве.
        account_id: Идентификатор аккаунта AmoCRM.
        statuses: Список статусов воронки.
    """

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
        """Создать экземпляр из словаря API."""
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
                else (
                    [PipelineStatus.from_dict(s) for s in statuses_raw]
                    if statuses_raw is not None
                    else None
                )
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для API, исключая поля со значением ``None``."""
        result: dict[str, Any] = {
            k: getattr(self, k)
            for k in _PIPELINE_SCALAR_FIELDS
            if getattr(self, k) is not None
        }
        if self.statuses is not None:
            result["_embedded"] = {"statuses": [s.to_dict() for s in self.statuses]}
        return result
