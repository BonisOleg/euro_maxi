from django import template
from django.utils.safestring import mark_safe

from content.sanitize import clean_page_html as _clean_page_html

register = template.Library()


@register.filter
def clean_page_html(value):
    """Повторна чистка на виході: старі рядки в БД теж не виконують скрипт."""
    return mark_safe(_clean_page_html(value))
