"""Кодогенератор типизированных DTO для кастомных полей AmoCRM.

Пример использования:

    from amocrm import OAuthConfig, DjangoTokenStorage
    from amocrm.codegen import generate_custom_fields_dto

    oauth = OAuthConfig(
        client_id="...",
        client_secret="...",
        redirect_uri="...",
        storage=DjangoTokenStorage(my_settings_obj),
    )
    generate_custom_fields_dto("mycompany", oauth, output_file="my_models.py")
"""

from __future__ import annotations

import keyword
import re
import sys

from .auth import OAuthConfig
from .client import AmoCRM
from .models.custom_fields import CustomFieldDefinition

_DEFAULT_ENTITIES = ["leads", "contacts", "companies"]

_ENTITY_CLASS_MAP: dict[str, str] = {
    "leads": "Lead",
    "contacts": "Contact",
    "companies": "Company",
}

_ENTITY_SUBCLASS_MAP: dict[str, str] = {
    "leads": "MyLead",
    "contacts": "MyContact",
    "companies": "MyCompany",
}

# (return_type, method, bool_special)
_TYPE_MAP: dict[str, tuple[str, str, bool]] = {
    "text": ("str | None", "get_cf_value", False),
    "textarea": ("str | None", "get_cf_value", False),
    "url": ("str | None", "get_cf_value", False),
    "phone": ("str | None", "get_cf_value", False),
    "email": ("str | None", "get_cf_value", False),
    "numeric": ("float | None", "get_cf_value", False),
    "monetary": ("float | None", "get_cf_value", False),
    "integer": ("int | None", "get_cf_value", False),
    "select": ("str | None", "get_cf_value", False),
    "radiobutton": ("str | None", "get_cf_value", False),
    "multiselect": ("list[str]", "get_cf_values", False),
    "checkbox": ("bool | None", "get_cf_value", True),
    "bool": ("bool | None", "get_cf_value", True),
    "date": ("int | None", "get_cf_value", False),
    "date_time": ("int | None", "get_cf_value", False),
    "birthday": ("int | None", "get_cf_value", False),
    "smart_address": ("dict[str, Any] | None", "get_cf_raw", False),
}

# Поля датаклассов Lead/Contact/Company — конфликты по имени нужно разрешать
_ENTITY_FIELDS: dict[str, frozenset[str]] = {
    "leads": frozenset(
        {
            "id",
            "name",
            "price",
            "status_id",
            "pipeline_id",
            "responsible_user_id",
            "group_id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "closed_at",
            "closest_task_at",
            "is_deleted",
            "loss_reason_id",
            "score",
            "account_id",
            "labor_cost",
            "tags",
            "custom_fields_values",
        }
    ),
    "contacts": frozenset(
        {
            "id",
            "name",
            "first_name",
            "last_name",
            "responsible_user_id",
            "group_id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "closest_task_at",
            "is_deleted",
            "account_id",
            "tags",
            "custom_fields_values",
        }
    ),
    "companies": frozenset(
        {
            "id",
            "name",
            "responsible_user_id",
            "group_id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "closest_task_at",
            "is_deleted",
            "account_id",
            "tags",
            "custom_fields_values",
        }
    ),
}


def _to_snake_case(name: str) -> str:
    """Преобразовать название поля в snake_case."""
    result = re.sub(r"[\s\-/\\]+", "_", name.strip())
    result = re.sub(r"[^\w]", "_", result)
    result = re.sub(r"_+", "_", result)
    result = result.strip("_").lower()
    return result or "field"


def _safe_prop_name(raw_name: str, entity: str, used: set[str]) -> str:
    """Вернуть безопасное имя property, избегая конфликтов."""
    snake = _to_snake_case(raw_name)
    reserved = _ENTITY_FIELDS.get(entity, frozenset())
    candidate = snake
    if keyword.iskeyword(candidate) or candidate in reserved or candidate in used:
        candidate = candidate + "_cf"
    # На случай если и с суффиксом конфликт
    while candidate in used:
        candidate = candidate + "_cf"
    used.add(candidate)
    return candidate


def _render_property(
    prop_name: str,
    field: CustomFieldDefinition,
    return_type: str,
    method: str,
    bool_special: bool,
) -> str:
    """Сгенерировать код property для одного поля."""
    docstring = f'"""{field.name} ({field.type}, id={field.id})"""'
    lines = [
        "    @property",
        f"    def {prop_name}(self) -> {return_type}:",
        f"        {docstring}",
    ]
    if bool_special:
        lines += [
            f"        v = self.{method}({field.id})",
            "        return bool(v) if v is not None else None",
        ]
    else:
        lines += [
            f"        return self.{method}({field.id})  # type: ignore[return-value]",
        ]
    return "\n".join(lines)


def fetch_custom_fields(
    client: AmoCRM,
    entities: list[str] | None = None,
) -> dict[str, list[CustomFieldDefinition]]:
    """Загрузить определения кастомных полей из AmoCRM для заданных сущностей.

    Args:
        client: Инициализированный клиент :class:`~amocrm.client.AmoCRM`.
        entities: Список типов сущностей. По умолчанию
            ``["leads", "contacts", "companies"]``.

    Returns:
        Словарь ``{entity: [CustomFieldDefinition, ...]}``.
    """
    if entities is None:
        entities = _DEFAULT_ENTITIES
    return {entity: client.custom_fields.list(entity) for entity in entities}


def generate_custom_models(
    fields_by_entity: dict[str, list[CustomFieldDefinition]],
    base_module: str = "amocrm",
) -> str:
    """Сгенерировать Python-код типизированных подклассов DTO.

    Args:
        fields_by_entity: Словарь ``{entity: [CustomFieldDefinition, ...]}``,
            полученный из :func:`fetch_custom_fields`.
        base_module: Имя модуля, из которого импортируются базовые классы.
            По умолчанию ``"amocrm"``.

    Returns:
        Строка с Python-кодом, готовая к записи в файл.
    """
    # Определяем, какие базовые классы нужны
    needed_bases: list[str] = []
    for entity in fields_by_entity:
        base = _ENTITY_CLASS_MAP.get(entity)
        if base and base not in needed_bases:
            needed_bases.append(base)

    needs_any = any(
        _TYPE_MAP.get(f.type, ("Any", "get_cf_value", False))[0]
        in ("dict[str, Any] | None", "Any")
        for fields in fields_by_entity.values()
        for f in fields
    )

    header_lines = [
        "# Generated by amocrm-sdk codegen. DO NOT EDIT.",
        "# Regenerate: from amocrm.codegen import generate_custom_fields_dto",
        "",
        "from __future__ import annotations",
        "",
    ]
    if needs_any:
        header_lines.append("from typing import Any")
        header_lines.append("")
    header_lines.append(f"from {base_module} import {', '.join(needed_bases)}")
    header_lines.append("")
    header_lines.append("")

    class_blocks: list[str] = []
    for entity, fields in fields_by_entity.items():
        base_class = _ENTITY_CLASS_MAP.get(entity)
        if not base_class:
            continue
        subclass_name = _ENTITY_SUBCLASS_MAP.get(entity, f"My{base_class}")
        docstring_entity = {
            "leads": "сделок",
            "contacts": "контактов",
            "companies": "компаний",
        }.get(entity, entity)

        class_lines = [
            f"class {subclass_name}({base_class}):",
            f'    """Типизированные кастомные поля для {docstring_entity}."""',
            "",
        ]

        used_names: set[str] = set()
        properties: list[str] = []
        for field_def in fields:
            return_type, method, bool_special = _TYPE_MAP.get(
                field_def.type, ("Any", "get_cf_value", False)
            )
            prop_name = _safe_prop_name(field_def.name, entity, used_names)
            prop_code = _render_property(
                prop_name, field_def, return_type, method, bool_special
            )
            properties.append(prop_code)

        if properties:
            class_lines.append("\n\n".join(properties))
        else:
            class_lines.append("    pass")

        class_blocks.append("\n".join(class_lines))

    return "\n".join(header_lines) + "\n\n".join(class_blocks) + "\n"


def generate_and_print(
    client: AmoCRM,
    entities: list[str] | None = None,
    base_module: str = "amocrm",
    output_file: str | None = None,
) -> None:
    """Получить кастомные поля и вывести/записать сгенерированный Python-код.

    Args:
        client: Инициализированный клиент :class:`~amocrm.client.AmoCRM`.
        entities: Список типов сущностей. По умолчанию
            ``["leads", "contacts", "companies"]``.
        base_module: Имя модуля для импорта базовых классов.
        output_file: Путь к файлу для записи. Если ``None`` — вывод в stdout.
    """
    fields_by_entity = fetch_custom_fields(client, entities)
    code = generate_custom_models(fields_by_entity, base_module)
    if output_file is None:
        sys.stdout.write(code)
    else:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(code)


def generate_custom_fields_dto(
    subdomain: str,
    oauth: OAuthConfig,
    entities: list[str] | None = None,
    base_module: str = "amocrm",
    output_file: str | None = None,
) -> None:
    """Подключиться к AmoCRM, получить кастомные поля и записать Python-код.

    Создаёт клиент, загружает определения кастомных полей и генерирует
    типизированные подклассы DTO для использования в проекте.

    Args:
        subdomain: Поддомен аккаунта AmoCRM (например, ``"mycompany"``).
        oauth: Конфигурация OAuth с реквизитами и хранилищем токенов.
        entities: Список сущностей для обработки. По умолчанию
            ``["leads", "contacts", "companies"]``.
        base_module: Имя модуля для импорта базовых классов.
            По умолчанию ``"amocrm"``.
        output_file: Путь к файлу для записи. Если ``None`` — вывод в stdout.

    Example::

        from amocrm import OAuthConfig, DjangoTokenStorage
        from amocrm.codegen import generate_custom_fields_dto

        oauth = OAuthConfig(
            client_id="...",
            client_secret="...",
            redirect_uri="...",
            storage=DjangoTokenStorage(my_settings_obj),
        )
        generate_custom_fields_dto("mycompany", oauth, output_file="my_models.py")
    """
    client = AmoCRM(subdomain, oauth)
    generate_and_print(client, entities, base_module, output_file)
