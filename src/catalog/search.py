"""Нормалізований пошук товарів: кирилиця, лапки, бренд і SKU."""
import re

from django.core.cache import cache
from django.db.models import Case, IntegerField, Value, When
from django.utils.html import strip_tags

_QUOTES_RE = re.compile(r"[«»\"'„“”‚‘’`]")
_FOLD = str.maketrans({"і": "и", "ї": "и", "є": "е", "ґ": "г"})

_SOURCE_FIELDS = frozenset(
    {"name", "sku", "short_description", "description", "brand", "brand_id"}
)

MAX_QUERY_LEN = 100
MAX_TOKENS = 6
MIN_TOKEN_LEN = 2
SUGGEST_LIMIT = 8
SUGGEST_RATE_LIMIT = 60
SUGGEST_RATE_WINDOW = 60


def normalize_search_text(text):
    if not text:
        return ""
    normalized = str(text).casefold()
    normalized = _QUOTES_RE.sub(" ", normalized)
    normalized = normalized.translate(_FOLD)
    return " ".join(normalized.split())


def _deduped(values):
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _plain(value):
    if not value:
        return ""
    return strip_tags(str(value))


def build_search_fields(product):
    name = normalize_search_text(getattr(product, "name", "") or "")
    brand_name = ""
    brand = getattr(product, "brand", None)
    if brand is not None:
        brand_name = normalize_search_text(getattr(brand, "name", "") or "")
    parts = _deduped(
        [
            name,
            brand_name,
            normalize_search_text(getattr(product, "sku", "") or ""),
            normalize_search_text(_plain(getattr(product, "short_description", ""))),
            normalize_search_text(_plain(getattr(product, "description", ""))),
        ]
    )
    return {"search_name": name, "search_text": " ".join(parts)}


def search_tokens(raw):
    normalized = normalize_search_text(raw)[:MAX_QUERY_LEN]
    return [token for token in normalized.split() if len(token) >= MIN_TOKEN_LEN][:MAX_TOKENS]


def apply_search(queryset, raw):
    """Фільтрує queryset і додає rank. Порядок не змінює."""
    tokens = search_tokens(raw)
    if not tokens:
        return queryset.annotate(rank=Value(3, output_field=IntegerField())).none()

    phrase = " ".join(tokens)
    query = queryset
    for token in tokens:
        query = query.filter(search_text__contains=token)

    stripped = " ".join(str(raw or "").split())[:MAX_QUERY_LEN]
    return query.annotate(
        rank=Case(
            When(sku__iexact=stripped, then=Value(0)),
            When(search_name__startswith=phrase, then=Value(1)),
            When(search_name__contains=phrase, then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        )
    )


def refresh_search_index(product):
    from catalog.models import Product

    Product.objects.filter(pk=product.pk).update(**build_search_fields(product))


def source_fields():
    return _SOURCE_FIELDS


def suggest_is_limited(request):
    ip = request.META.get("REMOTE_ADDR") or "unknown"
    key = f"search-suggest:{ip}"
    if cache.add(key, 1, SUGGEST_RATE_WINDOW):
        return False
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, SUGGEST_RATE_WINDOW)
        return False
    return count > SUGGEST_RATE_LIMIT
