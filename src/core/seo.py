"""Формування document title без подвійного суфікса бренду."""

SITE_BRAND = "Euromaxi UA"


def with_brand_suffix(page_title: str | None) -> str:
    title = (page_title or "").strip() or SITE_BRAND
    if SITE_BRAND in title:
        return title
    return f"{title} — {SITE_BRAND}"
