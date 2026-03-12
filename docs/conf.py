import os
import sys

# Добавляем src/ в путь, чтобы autodoc нашёл пакет amocrm
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
project = "amocrm-sdk"
author = "amocrm-sdk contributors"
release = "0.1.0"
language = "ru"

# -- Extensions --------------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",           # генерация API из docstrings
    "sphinx.ext.napoleon",          # поддержка Google-style docstrings
    "sphinx.ext.viewcode",          # ссылки на исходный код
    "sphinx.ext.intersphinx",       # ссылки на Python stdlib
]

# -- Napoleon settings (Google-style) ----------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_rtype = False          # тип возврата внутри Returns, не отдельно
napoleon_use_ivar = True            # :ivar: вместо .. attribute:: (нет конфликта с autodoc)

# -- Autodoc settings --------------------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "special-members": "__init__",
}
autodoc_typehints = "description"   # type hints в секции Parameters/Returns
autodoc_member_order = "bysource"   # порядок методов — как в исходнике

# Подавляем предупреждения о дубликатах (dataclass-поля реэкспортируются
# из amocrm/__init__.py и документируются дважды)

# -- Intersphinx -------------------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- HTML output -------------------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "navigation_depth": 3,
    "titles_only": False,
}
