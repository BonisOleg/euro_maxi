"""Продакшн: DigitalOcean + Docker + nginx + PostgreSQL."""
from decouple import config

from .base import *  # noqa: F401,F403

DEBUG = False

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SAMESITE = "Strict"
# HTTP-first (django-droplet-http-first): SECURE_SSL=False у .env, доки немає TLS.
# True лише після django-docker-ssl. Не хардкодити True — зламає сесію/адмінку по HTTP.
SESSION_COOKIE_SECURE = config("SECURE_SSL", default=True, cast=bool)
CSRF_COOKIE_SECURE = config("SECURE_SSL", default=True, cast=bool)
# TLS завершує nginx; Gunicorn лишається HTTP. True на web → healthz 301 → unhealthy.
SECURE_SSL_REDIRECT = config("SECURE_SSL", default=True, cast=bool)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)
