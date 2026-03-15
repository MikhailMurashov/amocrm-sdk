amocrm-sdk
==========

Python SDK для работы с REST API AmoCRM.
Предоставляет удобный интерфейс для авторизации, сделок, контактов,
компаний, задач и воронок.

Установка
---------

.. code-block:: bash

   pip install amocrm-sdk

Быстрый старт
-------------

.. code-block:: python

   from amocrm import AmoCRM, OAuthConfig, DjangoTokenStorage

   oauth = OAuthConfig(
       client_id="...",
       client_secret="...",
       redirect_uri="https://example.com/callback",
       storage=DjangoTokenStorage(my_model_instance),
   )

   client = AmoCRM(subdomain="mycompany", oauth=oauth)

   # Все сделки — авто-пагинация (Iterator, обходит все страницы)
   for lead in client.leads.list():
       print(lead.id, lead.name)

   # Одна страница — передайте page явно
   leads = client.leads.list(page=1, limit=50)

   # Создать контакт
   from amocrm import Contact
   contact = client.contacts.create([Contact(name="Иван Иванов")])[0]

.. toctree::
   :maxdepth: 2
   :caption: Документация

   leads
   pagination
   api
