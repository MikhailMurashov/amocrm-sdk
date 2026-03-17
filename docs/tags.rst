Теги (Tags)
===========

Теги доступны у сделок, контактов и компаний. Модель тега —
:class:`~amocrm.models.common.Tag` — содержит два поля: ``id`` и ``name``.

.. code-block:: python

   from amocrm import Tag

Чтение тегов
------------

При получении сущности из API теги автоматически парсятся из ``_embedded.tags``:

.. code-block:: python

   lead = client.leads.get(42)

   if lead.tags:
       for tag in lead.tags:
           print(tag.id, tag.name)

То же самое для контактов и компаний:

.. code-block:: python

   contact = client.contacts.get(10)
   company = client.companies.get(5)

   print(contact.tags)  # list[Tag] | None
   print(company.tags)  # list[Tag] | None

Создание сущности с тегами
--------------------------

Передайте список ``Tag`` при создании. Для новых тегов достаточно указать
только ``name`` — AmoCRM создаст тег автоматически:

.. code-block:: python

   from amocrm import Lead, Tag

   lead = Lead(
       name="Новая сделка",
       price=50000,
       tags=[Tag(name="vip"), Tag(name="горячий")],
   )
   created = client.leads.create([lead])

Чтобы привязать существующий тег, передайте его ``id``:

.. code-block:: python

   lead = Lead(
       name="Сделка с существующим тегом",
       tags=[Tag(id=12345)],
   )
   client.leads.create([lead])

Аналогично для контактов и компаний:

.. code-block:: python

   from amocrm import Contact, Company, Tag

   contact = Contact(
       name="Иван Иванов",
       tags=[Tag(name="важный клиент")],
   )
   client.contacts.create([contact])

   company = Company(
       name="ООО Ромашка",
       tags=[Tag(name="партнёр")],
   )
   client.companies.create([company])

Обновление тегов
----------------

Замена всех тегов
~~~~~~~~~~~~~~~~~

Присвойте новый список тегов и обновите сущность:

.. code-block:: python

   lead = client.leads.get(42)
   lead.tags = [Tag(name="vip"), Tag(name="приоритет")]
   client.leads.update_one(lead)

Добавление тега
~~~~~~~~~~~~~~~

Добавьте тег к существующему списку:

.. code-block:: python

   lead = client.leads.get(42)

   if lead.tags is None:
       lead.tags = []

   lead.tags.append(Tag(name="новый тег"))
   client.leads.update_one(lead)

Удаление тега
~~~~~~~~~~~~~

Отфильтруйте нужный тег из списка:

.. code-block:: python

   lead = client.leads.get(42)

   if lead.tags:
       lead.tags = [t for t in lead.tags if t.name != "горячий"]
       client.leads.update_one(lead)

Удаление всех тегов
~~~~~~~~~~~~~~~~~~~~

Передайте пустой список:

.. code-block:: python

   lead = client.leads.get(42)
   lead.tags = []
   client.leads.update_one(lead)

Фильтрация по тегам
--------------------

AmoCRM API позволяет фильтровать сущности по тегам через параметр ``filter``:

.. code-block:: python

   # По ID тега
   for lead in client.leads.list(filter={"tag_id": 12345}):
       print(lead.name)

   # По нескольким тегам (OR)
   for lead in client.leads.list(filter={"tag_id": [12345, 67890]}):
       print(lead.name)

Сериализация
------------

При вызове ``to_dict()`` теги помещаются на верхний уровень словаря
(а не в ``_embedded``). Это соответствует формату AmoCRM API для операций записи:

.. code-block:: python

   lead = Lead(
       name="Сделка",
       tags=[Tag(name="vip")],
   )
   lead.to_dict()
   # {"name": "Сделка", "tags": [{"name": "vip"}]}

Модель Tag
----------

.. autoclass:: amocrm.models.common.Tag
   :members:
   :undoc-members: