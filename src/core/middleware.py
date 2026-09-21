"""Дрібні middleware проєкту."""
from django.conf import settings


class AdminCSPRelaxMiddleware:
    """Знімає CSP з адмін-шляху (Unfold).

    Unfold ставить кольори в інлайн `<style id="unfold-theme-colors">` (~1400
    `var(--color-*)` у `styles.css`). `style-src 'self'` це блокує → HTML є,
    тема «гола». Alpine ще потребує eval + `element.style`. Вітрина без змін.

    Стоїть ПІСЛЯ `csp.middleware.CSPMiddleware`: `process_response` тут
    виконується раніше і ставить `_csp_exempt` до запису заголовка.
    """

    ADMIN_PREFIX = "/" + settings.ADMIN_URL.lstrip("/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(self.ADMIN_PREFIX):
            response._csp_exempt = True
        return response
