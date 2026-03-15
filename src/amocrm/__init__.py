"""AmoCRM Python SDK."""

from .auth import DjangoTokenStorage, InMemoryTokenStorage, OAuthConfig, TokenStorage
from .client import AmoCRM
from .codegen import generate_custom_fields_dto
from .exceptions import AmoCRMNotConfiguredError, AmoCRMTokenRefreshError
from .manager import exchange_code, get_client
from .models.common import CustomFieldsMixin, CustomFieldValue, Tag
from .models.companies import Company
from .models.contacts import Contact
from .models.custom_fields import CustomFieldDefinition, CustomFieldEnum
from .models.leads import Lead
from .models.pipelines import Pipeline, PipelineStatus, StatusDescription
from .models.tasks import Task

__version__ = "0.3.2"
__all__ = [
    "AmoCRM",
    "OAuthConfig",
    "TokenStorage",
    "InMemoryTokenStorage",
    "DjangoTokenStorage",
    "AmoCRMTokenRefreshError",
    "AmoCRMNotConfiguredError",
    "Lead",
    "Tag",
    "CustomFieldValue",
    "CustomFieldsMixin",
    "Contact",
    "Company",
    "Pipeline",
    "PipelineStatus",
    "StatusDescription",
    "Task",
    "CustomFieldDefinition",
    "CustomFieldEnum",
    "generate_custom_fields_dto",
    "exchange_code",
    "get_client",
]
