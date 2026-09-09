"""Налаштування для тестів: швидкі хешери, in-memory."""
from .base import *  # noqa: F401,F403

SECRET_KEY = "test-secret-key"
DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
