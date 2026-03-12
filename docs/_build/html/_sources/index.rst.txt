amocrm-sdk
==========

Python SDK для работы с REST API AmoCRM.
Предоставляет удобный интерфейс для авторизации, сделок, контактов,
компаний и воронок.

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

   # Список сделок
   leads = client.leads.list(limit=50)

   # Создать контакт
   from amocrm import Contact
   contact = client.contacts.create([Contact(name="Иван Иванов")])[0]

.. toctree::
   :maxdepth: 2
   :caption: Документация

   api
