"""Бізнес-логіка замовлень. Ціна ЗАВЖДИ береться з БД, ніколи з клієнта (SEC-02/06)."""
import logging

from django.db import transaction

from catalog.models import Product

from .models import Order, OrderItem

logger = logging.getLogger(__name__)


class CartValidationError(Exception):
    """Кошик містить недоступний товар — показати користувачу і попросити оновити кошик."""


@transaction.atomic
def create_order_from_cart(*, form_data: dict, cart_items: list[dict]) -> Order:
    merged = {}
    for item in cart_items:
        sku = item["sku"]
        merged[sku] = min(merged.get(sku, 0) + int(item["qty"]), 20)
    cart_items = [{"sku": sku, "qty": qty} for sku, qty in merged.items()]

    skus = [item["sku"] for item in cart_items]
    products = {p.sku: p for p in Product.objects.filter(sku__in=skus)}

    order = Order.objects.create(
        full_name=form_data["full_name"],
        phone=form_data["phone"],
        email=form_data.get("email", ""),
        comment=form_data.get("comment", ""),
        city=form_data["city"],
        np_type=form_data["np_type"],
        np_point=form_data["np_point"],
    )

    for item in cart_items:
        product = products.get(item["sku"])
        if product is None or not product.is_sellable:
            logger.warning(
                "Кошик містить недоступний товар sku=%s під час оформлення замовлення", item["sku"]
            )
            raise CartValidationError(
                f"Товар {item['sku']} більше не доступний. Оновіть кошик."
            )
        OrderItem.objects.create(
            order=order,
            product=product,
            product_sku=product.sku,
            product_name=str(product),
            unit_price_uah=product.price_uah,  # snapshot з БД, не з форми
            qty=item["qty"],
        )

    order.recalc_total()
    order.save(update_fields=["total_uah"])
    logger.info("Створено замовлення %s на суму %s UAH", order.order_number, order.total_uah)
    return order
