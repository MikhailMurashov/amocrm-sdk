# amocrm-sdk

Python SDK for the [AmoCRM REST API](https://www.amocrm.ru/developers/content/crm_platform/api-reference).

## Installation

```bash
uv add amocrm-sdk
# or
pip install amocrm-sdk
```

## Quick Start

### OAuth2 setup

```python
from amocrm import AmoCRM, OAuthConfig
from amocrm.auth import DjangoTokenStorage

oauth = OAuthConfig(
    client_id="...",
    client_secret="...",
    redirect_uri="https://yourapp.com/oauth/callback",
    storage=DjangoTokenStorage(AmoCRMToken.objects.get(id=1)),
)

# Первый запуск — обменять код авторизации на токены
client = AmoCRM.from_code(subdomain="your-company", code=auth_code, oauth=oauth)

# Последующие запуски — токены загружаются из storage автоматически
client = AmoCRM(subdomain="your-company", oauth=oauth)
```

### Глобальный менеджер (Django / Flask)

```python
from amocrm.manager import exchange_code, get_client

# OAuth callback view
exchange_code(subdomain="your-company", code=request.GET["code"], oauth=oauth)

# В любом месте приложения
client = get_client(subdomain="your-company", oauth=oauth)
```

### Кастомное хранилище токенов

```python
from amocrm import TokenStorage

class RedisTokenStorage:
    def save(self, access_token: str, refresh_token: str) -> None:
        redis.set("amo:access", access_token)
        redis.set("amo:refresh", refresh_token)

    def load(self) -> tuple[str, str]:
        return redis.get("amo:access"), redis.get("amo:refresh")
```

### Работа с ресурсами

```python
# Сделки
leads = client.leads.list(page=1, limit=50)
for lead in leads:
    print(lead.id, lead.name, lead.price)

lead = client.leads.get(42)
lead.price = 9000
client.leads.update_one(lead.id, lead)

new_lead = Lead(name="Big Deal", price=50000, tags=[Tag(name="vip")])
created = client.leads.create([new_lead])
print(created[0].id)

# Контакты
contacts = client.contacts.list(query="Иван")
client.contacts.create([Contact(name="Иван Иванов", first_name="Иван")])

# Компании
companies = client.companies.list(page=1, limit=25)
client.companies.create([Company(name="Рога и копыта")])
```

## Models

| Класс | Описание |
|-------|----------|
| `Lead` | Сделка. Поля: `id`, `name`, `price`, `status_id`, `pipeline_id`, `tags`, `custom_fields_values`, … |
| `Contact` | Контакт. Поля: `id`, `name`, `first_name`, `last_name`, `tags`, `custom_fields_values`, … |
| `Company` | Компания. Поля: `id`, `name`, `tags`, `custom_fields_values`, … |
| `Tag` | Тег. Поля: `id`, `name` |
| `CustomFieldValue` | Значение кастомного поля. Поля: `field_id`, `values` |
| `Pipeline` | Воронка. Поля: `id`, `name`, `statuses` |

Все модели — `@dataclass` с методами `from_dict` / `to_dict`. `to_dict()` исключает `None`-поля, что даёт чистый API payload.

## Features

- OAuth2 с auto-refresh токенов по 401
- Гибкое хранилище токенов — любой класс с `save()` / `load()` (Django ORM, Redis, etc.)
- `DjangoTokenStorage` из коробки
- Глобальный менеджер (`exchange_code` / `get_client`) для Django/Flask
- Typed DTO models — никаких сырых словарей
- Leads (сделки): list, get, create, update, update_one, create_complex
- Contacts (контакты): list, get, create, update, update_one
- Companies (компании): list, get, create, update, update_one
- Pipelines (воронки): list, get, create, update, delete + statuses CRUD
- Custom fields support
- Pagination helpers

## Links

- [AmoCRM API Reference](https://www.amocrm.ru/developers/content/crm_platform/api-reference)
- [OAuth2 guide](https://www.amocrm.ru/developers/content/oauth/oauth)


# TODO

- https://www.amocrm.ru/developers/content/api/recommendations
- https://www.amocrm.ru/developers/content/crm_platform/account-info
- ~~https://www.amocrm.ru/developers/content/crm_platform/leads-api~~
- https://www.amocrm.ru/developers/content/crm_platform/unsorted-api
- ~~https://www.amocrm.ru/developers/content/crm_platform/leads_pipelines~~
- https://www.amocrm.ru/developers/content/crm_platform/filters-api
- ~~https://www.amocrm.ru/developers/content/crm_platform/contacts-api~~
- ~~https://www.amocrm.ru/developers/content/crm_platform/companies-api~~
- https://www.amocrm.ru/developers/content/crm_platform/catalogs-api
- https://www.amocrm.ru/developers/content/crm_platform/entity-links-api
- https://www.amocrm.ru/developers/content/crm_platform/tasks-api
- https://www.amocrm.ru/developers/content/crm_platform/custom-fields
- https://www.amocrm.ru/developers/content/crm_platform/tags-api
- https://www.amocrm.ru/developers/content/crm_platform/events-and-notes
- https://www.amocrm.ru/developers/content/crm_platform/customers-api
- https://www.amocrm.ru/developers/content/crm_platform/customers-statuses-api
- https://www.amocrm.ru/developers/content/crm_platform/users-api
- https://www.amocrm.ru/developers/content/crm_platform/products-api
- https://www.amocrm.ru/developers/content/crm_platform/webhooks-api
- https://www.amocrm.ru/developers/content/crm_platform/widgets-api
- https://www.amocrm.ru/developers/content/crm_platform/calls-api
- https://www.amocrm.ru/developers/content/crm_platform/talks-api
- https://www.amocrm.ru/developers/content/crm_platform/subscriptions-api
- https://www.amocrm.ru/developers/content/crm_platform/sources-api
- https://www.amocrm.ru/developers/content/api/salesbot-api
- https://www.amocrm.ru/developers/content/crm_platform/short_links
- https://www.amocrm.ru/developers/content/crm_platform/chat-templates-api
- https://www.amocrm.ru/developers/content/crm_platform/duplication-control
