"""Спільні налаштування Euromaxi UA (усі середовища)."""
from pathlib import Path

from decouple import Csv, config

# config/settings/base.py -> .parent (settings) -> .parent (config) -> .parent (корінь проєкту)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"

SECRET_KEY = config("SECRET_KEY")  # без default — production падає без .env

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",  # WYSIWYG (Trix) для текстових полів статичних сторінок
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "csp",
    # Euromaxi UA apps
    "core",
    "catalog",
    "commerce",
    "content",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "csp.middleware.CSPMiddleware",
    # ПІСЛЯ CSPMiddleware (SEC/CSP): послаблює script-src лише для /ADMIN_URL/.
    "core.middleware.AdminCSPRelaxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",
                "core.context_processors.cart_catalog",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="euromaxi"),
        "USER": config("POSTGRES_USER", default="euromaxi"),
        "PASSWORD": config("POSTGRES_PASSWORD", default=""),
        "HOST": config("POSTGRES_HOST", default="db"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Одномовний сайт (ТЗ п.5.3 — модуль багатомовності не передбачений)
LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = False
USE_TZ = True

# Static — одне дерево (ERR-138): усе статичне у src/core/static/, AppDirectoriesFinder
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Cache-bust для локальної розробки (у prod ManifestStaticFilesStorage дає хеш у імені).
STATIC_ASSET_VERSION = config("STATIC_ASSET_VERSION", default="20260921a")
STATICFILES_DIRS = []
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# LS-30: узгоджено з nginx `client_max_body_size 20M` (deploy/nginx/default.conf) —
# інакше Django за замовчуванням (2.5 МБ) відрізає завантаження фото товарів в адмінці
# раніше, ніж запит навіть дійде до nginx-лімітів.
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Адмінка не на /admin/ (SEC-08, ERR-132)
ADMIN_URL = config("ADMIN_URL", default="admin/")

# Кастомний ADMIN_URL з env (SEC-08 / ERR-132)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()],
)

# --- Логування (з першого дня) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "core": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "catalog": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "commerce": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "content": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

# --- CSP (django-csp==4.0, з першого дня) ---
# Unfold інлайн-тема (`<style id="unfold-theme-colors">`) + Alpine eval/style.
# Виключення лише адмінки; вітрина лишається зі строгим style-src.
_ADMIN_CSP_PREFIX = "/" + str(ADMIN_URL).strip("/") + "/"
CONTENT_SECURITY_POLICY = {
    "EXCLUDE_URL_PREFIXES": (_ADMIN_CSP_PREFIX,),
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "style-src": ["'self'", "https://fonts.googleapis.com"],
        "font-src": ["'self'", "https://fonts.gstatic.com"],
        "img-src": ["'self'", "data:"],
        "connect-src": ["'self'"],
        "frame-ancestors": ["'none'"],
    },
}
# Unfold/Alpine.js в адмінці потребує unsafe-eval — виключення лише для адмін-шляху
CONTENT_SECURITY_POLICY_REPORT_ONLY = None

# --- Euromaxi UA — бізнес-налаштування ---
# Monobank: sandbox-режим, доки клієнт не надасть токен (ТЗ п.4.4)
MONOBANK_TOKEN = config("MONOBANK_TOKEN", default="")
MONOBANK_WEBHOOK_SECRET = config("MONOBANK_WEBHOOK_SECRET", default="")

# Нова Пошта: Фаза 0.5 stub, доки клієнт не надасть API-ключ (ТЗ п.4.4)
NOVA_POSHTA_API_KEY = config("NOVA_POSHTA_API_KEY", default="")

# EUR->UAH перерахунок цін (recalc_prices command) — курс/націнку підтверджує клієнт
DEFAULT_EUR_UAH_RATE = config("DEFAULT_EUR_UAH_RATE", default=0.0, cast=float)
DEFAULT_MARKUP_PERCENT = config("DEFAULT_MARKUP_PERCENT", default=0.0, cast=float)

# --- django-unfold ---
from django.urls import reverse_lazy as _reverse_lazy  # noqa: E402

UNFOLD = {
    "SITE_TITLE": "Euromaxi UA — адмінка",
    "SITE_HEADER": "Euromaxi UA",
    "SHOW_HISTORY": True,
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": "Каталог",
                "items": [
                    {
                        "title": "Бренди",
                        "icon": "sell",
                        "link": _reverse_lazy("admin:catalog_brand_changelist"),
                    },
                    {
                        "title": "Товари",
                        "icon": "inventory_2",
                        "link": _reverse_lazy("admin:catalog_product_changelist"),
                    },
                ],
            },
            {
                "title": "Замовлення",
                "items": [
                    {
                        "title": "Замовлення",
                        "icon": "shopping_cart",
                        "link": _reverse_lazy("admin:commerce_order_changelist"),
                    },
                ],
            },
            {
                "title": "Контент",
                "items": [
                    {
                        "title": "Сторінки",
                        "icon": "description",
                        "link": _reverse_lazy("admin:content_page_changelist"),
                    },
                    {
                        "title": "Звернення",
                        "icon": "mail",
                        "link": _reverse_lazy("admin:content_contactmessage_changelist"),
                    },
                    {
                        "title": "Налаштування сайту",
                        "icon": "settings",
                        "link": _reverse_lazy("admin:content_sitesettings_changelist"),
                    },
                ],
            },
        ],
    },
}
