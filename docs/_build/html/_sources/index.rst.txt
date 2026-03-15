amocrm-sdk
==========

Python SDK для работы с REST API AmoCRM.
Предоставляет удобный интерфейс для авторизации, сделок, контактов,
компаний, задач и воронок.

Установка
---------

.. code-block:: bash

   pip install amocrm-sdk

Типичный порядок работы
-----------------------

.. code-block:: python

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

   # 3. Получение лида с контактом и компанией (contacts подгружаются по умолчанию)
   lead = client.leads.get(lead_id)
   contact = lead.contacts[0]   # Contact
   company = lead.company        # Company

   # 4. Обновление контакта
   contact.name = "Иван Петров"
   client.contacts.update_one(contact.id, contact)

   # 5. Обновление компании
   company.name = "ООО Лютик"
   client.companies.update_one(company.id, company)

Работа с ресурсами
------------------

.. code-block:: python

   # Сделки — авто-пагинация (обходит все страницы, возвращает Iterator)
   for lead in client.leads.list():
       print(lead.id, lead.name, lead.price)

   # Одна страница — передайте page явно
   leads = client.leads.list(page=1, limit=50)

   # get() автоматически подгружает контакты (with=contacts по умолчанию)
   lead = client.leads.get(42)
   print(lead.contacts)       # list[Contact] | None
   lead.price = 9000
   client.leads.update_one(lead.id, lead)

   new_lead = Lead(name="Big Deal", price=50000, tags=[Tag(name="vip")])
   created = client.leads.create([new_lead])
   print(created[0].id)

   # Создать сделку вместе с контактом и компанией (max 1 контакт, max 50 сделок)
   from amocrm import Contact, Company
   lead = Lead(
       name="Complex Deal",
       contacts=[Contact(name="Иван Иванов")],
       company=Company(name="ООО Ромашка"),
   )
   client.leads.create_complex([lead])

   # Контакты — авто-пагинация
   for contact in client.contacts.list(query="Иван"):
       print(contact.name)

   client.contacts.create([Contact(name="Иван Иванов", first_name="Иван")])

   # Компании — авто-пагинация
   for company in client.companies.list():
       print(company.name)

   client.companies.create([Company(name="Рога и копыта")])

   # Задачи — авто-пагинация
   from amocrm import Task

   for task in client.tasks.list():
       print(task.id, task.text, task.complete_till)

   task = client.tasks.get(10)
   task.text = "Updated text"
   client.tasks.update_one(task.id, task)

   new_task = Task(text="Call client", task_type_id=1, complete_till=1700000000, entity_id=lead.id, entity_type="leads")
   created = client.tasks.create([new_task])
   print(created[0].id)

Пагинация
---------

Методы ``list()`` у всех ресурсов поддерживают два режима:

.. list-table::
   :header-rows: 1

   * - Вызов
     - Поведение
     - Возвращает
   * - ``client.leads.list()``
     - Авто-пагинация — обходит все страницы
     - ``Iterator[Lead]``
   * - ``client.leads.list(page=2)``
     - Одна конкретная страница
     - ``list[Lead]``

По умолчанию авто-пагинация запрашивает по **50 элементов** на страницу.
Для кастомного размера: ``client.leads.list(limit=250)``.

.. toctree::
   :maxdepth: 2
   :caption: Документация

   leads
   pagination
   codegen
   api
