import logging

from django.db.models.signals import post_save

from catalog.search import refresh_search_index, source_fields

logger = logging.getLogger(__name__)


def on_product_save(sender, instance, raw=False, update_fields=None, **kwargs):
    if raw:
        return
    if update_fields is not None and source_fields().isdisjoint(update_fields):
        return
    try:
        refresh_search_index(instance)
    except Exception:
        logger.exception("Індекс пошуку не оновлено для товару %s", instance.pk)


def on_brand_save(sender, instance, raw=False, **kwargs):
    if raw:
        return
    try:
        for product in instance.products.select_related("brand"):
            refresh_search_index(product)
    except Exception:
        logger.exception("Індекс пошуку не оновлено для бренду %s", instance.pk)


def connect_search_signals():
    from catalog.models import Brand, Product

    post_save.connect(on_product_save, sender=Product, dispatch_uid="catalog-product-search")
    post_save.connect(on_brand_save, sender=Brand, dispatch_uid="catalog-brand-search")
