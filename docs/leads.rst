Сделки (Leads)
==============

Ресурс ``client.leads`` предоставляет полный набор методов для работы со сделками AmoCRM.

Получение сделок
----------------

Список сделок
~~~~~~~~~~~~~

.. code-block:: python

   leads = client.leads.list(page=1, limit=50)

Доступные параметры:

- ``page`` — номер страницы (начиная с 1)
- ``limit`` — количество сделок на странице (максимум 250)
- ``query`` — строка полнотекстового поиска
- ``filter`` — словарь фильтров: ``{"status_id": 123}`` → ``filter[status_id]=123``
- ``order`` — словарь сортировки: ``{"created_at": "desc"}``
- ``with_`` — дополнительные связанные данные (см. ниже)

Одна сделка по ID
~~~~~~~~~~~~~~~~~

.. code-block:: python

   lead = client.leads.get(42)

По умолчанию ``get()`` автоматически добавляет ``with=contacts``, поэтому
поле ``lead.contacts`` будет заполнено без дополнительных параметров.

Чтобы отключить подгрузку контактов, передайте пустой список:

.. code-block:: python

   lead = client.leads.get(42, with_=[])

Чтобы запросить дополнительные данные, передайте нужные ключи явно:

.. code-block:: python

   lead = client.leads.get(42, with_=["contacts", "loss_reason"])

Создание и обновление
---------------------

.. code-block:: python

   from amocrm import Lead

   # Создать одну или несколько сделок (не более 50 за запрос)
   new_leads = client.leads.create([
       Lead(name="Новая сделка", price=5000, status_id=1234),
   ])

   # Обновить (не более 50 за запрос, каждая сделка должна содержать id)
   client.leads.update([Lead(id=10, price=9000)])

   # Обновить одну сделку по ID
   client.leads.update_one(10, Lead(price=9000))

.. warning::

   За один запрос можно передать не более **50 сделок**. При превышении
   лимита выбрасывается :class:`~amocrm.exceptions.AmoCRMError`.

Связанные сущности: контакты и компании
---------------------------------------

Загрузка при чтении
~~~~~~~~~~~~~~~~~~~

``get()`` подгружает контакты автоматически (``with=contacts`` по умолчанию).
Для компаний добавьте ``"companies"`` явно:

.. code-block:: python

   lead = client.leads.get(42, with_=["contacts", "companies"])

   if lead.contacts:
       for contact in lead.contacts:
           print(contact.id, contact.name)

   if lead.company:
       print(lead.company.id, lead.company.name)

Поля модели :class:`~amocrm.models.leads.Lead`:

- ``contacts: list[Contact] | None`` — список связанных контактов
  (API может вернуть несколько)
- ``company: Company | None`` — первая связанная компания
  (берётся ``_embedded.companies[0]``)

Создание сделок со связанными сущностями (complex)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Эндпоинт ``POST /api/v4/leads/complex`` позволяет за один запрос
создать сделку вместе с контактом и компанией:

.. code-block:: python

   from amocrm import Lead, Contact, Company

   lead = Lead(
       name="Комплексная сделка",
       price=15000,
       contacts=[Contact(name="Иван Иванов", first_name="Иван")],
       company=Company(name="ООО Ромашка"),
   )

   result = client.leads.create_complex([lead])

Ограничения ``create_complex``:

- не более **50 сделок** за запрос
- не более **1 контакта** на сделку

При нарушении любого ограничения выбрасывается
:class:`~amocrm.exceptions.AmoCRMError` до отправки запроса.

Сериализация в ``to_dict``
~~~~~~~~~~~~~~~~~~~~~~~~~~

При передаче в API контакты и компания попадают в ключ ``_embedded``:

.. code-block:: python

   lead = Lead(
       name="Сделка",
       contacts=[Contact(id=5)],
       company=Company(id=10),
   )
   lead.to_dict()
   # {
   #     "name": "Сделка",
   #     "_embedded": {
   #         "contacts": [{"id": 5}],
   #         "companies": [{"id": 10}],
   #     }
   # }

.. note::

   Теги (``tags``) остаются на верхнем уровне словаря — это соглашение
   AmoCRM API для операций записи. Связанные сущности (контакты, компании)
   при записи передаются через ``_embedded``.

Обработка ошибок
----------------

.. code-block:: python

   from amocrm.exceptions import AmoCRMError, AmoCRMAPIError

   try:
       client.leads.create([Lead(name=f"Deal {i}") for i in range(51)])
   except AmoCRMError as e:
       print(e)  # create allows at most 50 leads per request

   try:
       lead = Lead(contacts=[Contact(id=1), Contact(id=2)])
       client.leads.create_complex([lead])
   except AmoCRMError as e:
       print(e)  # create_complex allows at most 1 contact per lead
