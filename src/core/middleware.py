"""Дрібні middleware проєкту."""
from django.conf import settings


class AdminCSPRelaxMiddleware:
    """Послаблює `script-src` CSP лише для адмін-шляху.

    Unfold (Alpine.js) потребує `unsafe-eval` для роботи UI. У `develop.py` CSP
    вже послаблена глобально (нема сенсу обмежувати локально), але на проді
    (`production.py`) CSP лишається строгою (`'self'`) для вітрини — і без
    цього middleware адмінка була б зламана суворим CSP.

    ВАЖЛИВО: цей middleware має стояти ПІСЛЯ `csp.middleware.CSPMiddleware` у
    `MIDDLEWARE`, щоб його `process_response` (виконується "зсередини назовні",
    тобто раніше за CSPMiddleware) встиг проставити `response._csp_update` до
    того, як `CSPMiddleware` формує заголовок `Content-Security-Policy`.
    """

    ADMIN_PREFIX = "/" + settings.ADMIN_URL.lstrip("/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(self.ADMIN_PREFIX):
            # Ключ у форматі CSP-директиви ("script-src"), як у CONTENT_SECURITY_POLICY —
            # інакше django-csp додає ЩЕ ОДНУ окрему (неправильну) директиву в заголовок,
            # замість об'єднання зі значенням 'self' з базового конфігу.
            response._csp_update = {"script-src": ["'unsafe-eval'"]}
        return response
