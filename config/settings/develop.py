"""Локальна розробка: SQLite за замовчуванням, DEBUG=True."""
from decouple import config

from .base import *  # noqa: F401,F403

SECRET_KEY = config("SECRET_KEY", default="dev-only-insecure-key-do-not-use-in-prod")

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Локально — SQLite, щоб не тримати Postgres запущеним для швидкого старту.
# Якщо в .env задано POSTGRES_HOST — використовується Postgres (для паритету з prod).
if not config("POSTGRES_HOST", default=""):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# CSP у develop — дозволяємо unsafe-eval для Unfold/Alpine.js без окремого report-only шару
CONTENT_SECURITY_POLICY["DIRECTIVES"]["script-src"] = ["'self'", "'unsafe-eval'"]  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
