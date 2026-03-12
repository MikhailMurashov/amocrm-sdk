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

# List leads
leads = client.leads.list()
for lead in leads:
    print(lead["id"], lead["name"])
```

## Features

- OAuth2 token-based authentication
- Leads (сделки)
- Contacts (контакты)
- Companies (компании)
- Custom fields support
- Pagination helpers

## Links

- [AmoCRM API Reference](https://www.amocrm.ru/developers/content/crm_platform/api-reference)
- [OAuth2 guide](https://www.amocrm.ru/developers/content/oauth/oauth)
