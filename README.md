# amocrm-sdk

[![PyPI](https://img.shields.io/pypi/v/amocrm-sdk)](https://pypi.org/project/amocrm-sdk/)
[![Docs](https://readthedocs.org/projects/amocrm-sdk/badge/?version=latest)](https://amocrm-sdk.readthedocs.io)

Python SDK for the [AmoCRM REST API](https://www.amocrm.ru/developers/content/crm_platform/api-reference).

## Features

- OAuth2 с auto-refresh токенов по 401
- Гибкое хранилище токенов — любой класс с `save()` / `load()` (Django ORM, Redis, etc.)
- `DjangoTokenStorage` из коробки
- Глобальный менеджер (`exchange_code` / `get_client`) для Django/Flask
- Typed DTO models — никаких сырых словарей
- Leads (сделки): list, get, create, update, update_one, create_complex; `get()` подгружает контакты по умолчанию; лимит 50 сделок за запрос
- Contacts (контакты): list, get, create, update, update_one
- Companies (компании): list, get, create, update, update_one
- Pipelines (воронки): list, get, create, update, delete + statuses CRUD
- Tasks (задачи): list, get, create, update, update_one
- Custom fields support
- Авто-пагинация — `list()` без `page` автоматически обходит все страницы и возвращает `Iterator[T]`
- Кастомные DTO — `configure_dto()` позволяет подменить базовые классы своими подклассами

## Installation

```bash
uv add amocrm-sdk
# or
pip install amocrm-sdk
```

## Quick Start

### OAuth2 setup

```python
from amocrm import OAuthConfig
from amocrm.auth import DjangoTokenStorage
from amocrm.manager import exchange_code, get_client

oauth = OAuthConfig(
    client_id="...",
    client_secret="...",
    redirect_uri="https://yourapp.com/oauth/callback",
    storage=DjangoTokenStorage(AmoCRMToken.objects.get(id=1)),
)

# Первый запуск — обменять код авторизации на токены
exchange_code(subdomain="your-company", code=auth_code, oauth=oauth)

# Последующие запуски — токены загружаются из storage автоматически
client = get_client(subdomain="your-company", oauth=oauth)
```

### Кастомное хранилище токенов

```python
# Пример с Redis
class RedisTokenStorage:
    def save(self, access_token: str, refresh_token: str) -> None:
        redis.set("amo:access", access_token)
        redis.set("amo:refresh", refresh_token)

    def load(self) -> tuple[str, str]:
        return redis.get("amo:access"), redis.get("amo:refresh")
```

### Типичный порядок работы

```python
from amocrm import OAuthConfig, Lead, Contact, Company
from amocrm.auth import DjangoTokenStorage
from amocrm.manager import exchange_code, get_client

oauth = OAuthConfig(
    client_id="...",
    client_secret="...",
    redirect_uri="https://yourapp.com/oauth/callback",
    storage=DjangoTokenStorage(AmoCRMToken.objects.get(id=1)),
)

# 1. Обмен кода авторизации на токены (OAuth callback)
exchange_code(subdomain="your-company", code=auth_code, oauth=oauth)
client = get_client(subdomain="your-company", oauth=oauth)

# 2. Создание сделки с контактом и компанией (create_complex)
lead = Lead(
    name="Новая сделка",
    price=100000,
    contacts=[Contact(name="Иван Иванов")],
    company=Company(name="ООО Ромашка"),
)
created = client.leads.create_complex([lead])
lead_id = created[0].id

# 3. Получение лида с контактом и компанией (get подгружает contacts по умолчанию)
lead = client.leads.get(lead_id)
contact = lead.contacts[0]  # Contact
company = lead.company      # Company

# 4. Обновление контакта
contact.name = "Иван Петров"
client.contacts.update_one(contact.id, contact)

# 5. Обновление компании
company.name = "ООО Лютик"
client.companies.update_one(company.id, company)
```

### Пагинация

Методы `list()` у всех ресурсов поддерживают два режима:

| Вызов | Поведение | Возвращает |
|-------|-----------|------------|
| `client.leads.list()` | Авто-пагинация — обходит все страницы | `Iterator[Lead]` |
| `client.leads.list(page=2)` | Одна конкретная страница | `list[Lead]` |

По умолчанию авто-пагинация запрашивает по **50 элементов** на страницу. Для кастомного размера: `client.leads.list(limit=250)`.

### Кодогенератор (Codegen)

Генерирует типизированные подклассы DTO с named-свойствами для кастомных полей AmoCRM.
Имена свойств автоматически транслитерируются из кириллицы в латиницу.

```python
from amocrm import OAuthConfig, DjangoTokenStorage
from amocrm.codegen import generate_custom_fields_dto

oauth = OAuthConfig(client_id="...", client_secret="...", redirect_uri="...",
                    storage=DjangoTokenStorage(django_obj))
generate_custom_fields_dto("mycompany", oauth, output_file="src/amocrm/models/my_models.py")
```

### Подключение кастомных DTO

После кодогенерации подключите свои классы к клиенту через `configure_dto()` — все методы
`get`, `list`, `create`, `update` начнут возвращать экземпляры вашего подкласса:

```python
from amocrm.models.my_models import MyLead, MyContact, MyCompany

client = get_client(subdomain="mycompany", oauth=oauth)
client.configure_dto(leads=MyLead, contacts=MyContact, companies=MyCompany)

lead = client.leads.get(123)  # → MyLead
lead.inn  # → str | None  (геттер из MyLead)

lead.inn = "new_inn"  # записывает в custom_fields_values
client.leads.update([lead])  # сохраняет изменения в AmoCRM

for lead in client.leads.list():
    print(lead.istochnik_trafika)  # → str | None
```

Подробнее — в [документации](https://amocrm-sdk.readthedocs.io/en/latest/codegen.html).

## Links

- [PyPI](https://pypi.org/project/amocrm-sdk/)
- [Documentation](https://amocrm-sdk.readthedocs.io)
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
- ~~https://www.amocrm.ru/developers/content/crm_platform/tasks-api~~
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
