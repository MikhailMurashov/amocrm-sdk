# amocrm-sdk

Python SDK for the [AmoCRM REST API](https://www.amocrm.ru/developers/content/crm_platform/api-reference).

## Installation

```bash
uv add amocrm-sdk
# or
pip install amocrm-sdk
```

## Quick Start

```python
from amocrm import AmoCRM

client = AmoCRM(
    subdomain="your-company",
    access_token="your_access_token",
)

# Список сделок — возвращает list[Lead]
leads = client.leads.list(page=1, limit=50)
for lead in leads:
    print(lead.id, lead.name, lead.price)

# Получить одну сделку и изменить поле
lead = client.leads.get(42)
lead.price = 9000
client.leads.update_one(lead.id, lead)

# Создать сделку
from amocrm import Lead, Tag

new_lead = Lead(
    name="Big Deal",
    price=50000,
    tags=[Tag(name="vip")],
)
created = client.leads.create([new_lead])
print(created[0].id)
```

## Models

| Класс | Описание |
|-------|----------|
| `Lead` | Сделка. Поля: `id`, `name`, `price`, `status_id`, `pipeline_id`, `tags`, `custom_fields_values`, … |
| `Tag` | Тег сделки. Поля: `id`, `name` |
| `CustomFieldValue` | Значение кастомного поля. Поля: `field_id`, `values` |

Все модели — `@dataclass` с методами `from_dict` / `to_dict`. `to_dict()` исключает `None`-поля, что даёт чистый API payload.

## Features

- OAuth2 token-based authentication
- Typed DTO models (`Lead`, `Tag`, `CustomFieldValue`) — никаких сырых словарей
- Leads (сделки): list, get, create, update, update_one, create_complex
- Custom fields support
- Pagination helpers

## Links

- [AmoCRM API Reference](https://www.amocrm.ru/developers/content/crm_platform/api-reference)
- [OAuth2 guide](https://www.amocrm.ru/developers/content/oauth/oauth)


TODO:

https://www.amocrm.ru/developers/content/api/recommendations
https://www.amocrm.ru/developers/content/crm_platform/account-info
~~https://www.amocrm.ru/developers/content/crm_platform/leads-api~~
https://www.amocrm.ru/developers/content/crm_platform/unsorted-api
https://www.amocrm.ru/developers/content/crm_platform/leads_pipelines
https://www.amocrm.ru/developers/content/crm_platform/filters-api
https://www.amocrm.ru/developers/content/crm_platform/contacts-api
https://www.amocrm.ru/developers/content/crm_platform/companies-api
https://www.amocrm.ru/developers/content/crm_platform/catalogs-api
https://www.amocrm.ru/developers/content/crm_platform/entity-links-api
https://www.amocrm.ru/developers/content/crm_platform/tasks-api
https://www.amocrm.ru/developers/content/crm_platform/custom-fields
https://www.amocrm.ru/developers/content/crm_platform/tags-api
https://www.amocrm.ru/developers/content/crm_platform/events-and-notes
https://www.amocrm.ru/developers/content/crm_platform/customers-api
https://www.amocrm.ru/developers/content/crm_platform/customers-statuses-api
https://www.amocrm.ru/developers/content/crm_platform/users-api
https://www.amocrm.ru/developers/content/crm_platform/products-api
https://www.amocrm.ru/developers/content/crm_platform/webhooks-api
https://www.amocrm.ru/developers/content/crm_platform/widgets-api
https://www.amocrm.ru/developers/content/crm_platform/calls-api
https://www.amocrm.ru/developers/content/crm_platform/talks-api
https://www.amocrm.ru/developers/content/crm_platform/subscriptions-api
https://www.amocrm.ru/developers/content/crm_platform/sources-api
https://www.amocrm.ru/developers/content/api/salesbot-api
https://www.amocrm.ru/developers/content/crm_platform/short_links
https://www.amocrm.ru/developers/content/crm_platform/chat-templates-api
https://www.amocrm.ru/developers/content/crm_platform/duplication-control
