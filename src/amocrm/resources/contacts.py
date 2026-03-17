from __future__ import annotations

from ..models.contacts import Contact
from ._base import BaseResource


class ContactsResource(BaseResource[Contact]):
    """Ресурс для работы с контактами AmoCRM (``/api/v4/contacts``)."""

    _path = "/api/v4/contacts"
    _embedded_key = "contacts"
    _dto_class = Contact
