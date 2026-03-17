from __future__ import annotations

from ..models.companies import Company
from ._base import BaseResource


class CompaniesResource(BaseResource[Company]):
    """Ресурс для работы с компаниями AmoCRM (``/api/v4/companies``)."""

    _path = "/api/v4/companies"
    _embedded_key = "companies"
    _dto_class = Company
