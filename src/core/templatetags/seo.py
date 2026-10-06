from django import template

from core.seo import with_brand_suffix as _with_brand_suffix

register = template.Library()


@register.filter
def with_brand_suffix(value):
    return _with_brand_suffix(value)
