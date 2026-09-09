"""Глобальний контекст для всіх шаблонів (телефон, email, реквізити, кошик)."""
from django.conf import settings

from catalog.models import Product
from content.models import SiteSettings


def site_settings(request):
    """Дає доступ до SiteSettings (singleton) у будь-якому шаблоні як {{ site }}."""
    return {
        "site": SiteSettings.get_solo(),
        "STATIC_ASSET_VERSION": getattr(settings, "STATIC_ASSET_VERSION", "1"),
    }


def cart_catalog(request):
    """Мінімальний каталог активних товарів для client-side кошика (localStorage).

    Кошик і сума в UI рахуються на фронті лише для відображення (js/cart.js) —
    сервер на checkout ПОВНІСТЮ перераховує ціну з БД (SEC-02), тому довіра
    до цього JSON на клієнті не є проблемою безпеки.
    """
    products = []
    for p in Product.objects.filter(is_active=True).select_related("brand").prefetch_related(
        "images"
    ):
        image = p.primary_image
        products.append(
            {
                "sku": p.sku,
                "brand": p.brand.name,
                "name": str(p),
                "short": p.short_description,
                "price": float(p.price_uah) if p.price_uah else 0,
                "oldPrice": float(p.old_price_uah) if p.old_price_uah else None,
                "image": image.image.url if image else "",
                "url": p.get_absolute_url(),
            }
        )
    return {"cart_catalog_json": products}
