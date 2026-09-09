import uuid

from django.db import models


class NovaPoshtaType(models.TextChoices):
    WAREHOUSE = "warehouse", "Відділення"
    POSTOMAT = "postomat", "Поштомат"
    ADDRESS = "address", "Адресна доставка"


class PaymentMethod(models.TextChoices):
    MONOBANK = "monobank", "Monobank"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Очікує оплати"
    PAID = "paid", "Оплачено"
    FAILED = "failed", "Помилка оплати"


class OrderStatus(models.TextChoices):
    NEW = "new", "Нове"
    CONFIRMED = "confirmed", "Підтверджено"
    SHIPPED = "shipped", "Відправлено"
    DONE = "done", "Виконано"
    CANCELLED = "cancelled", "Скасовано"


class Order(models.Model):
    """Замовлення. Ціни в OrderItem — snapshot на момент оформлення (SEC-06)."""

    order_number = models.CharField(
        "Номер замовлення", max_length=20, unique=True, editable=False
    )

    # --- Покупець (ТЗ: ПІБ, телефон обов'язкові; email опціонально) ---
    full_name = models.CharField("ПІБ", max_length=150)
    phone = models.CharField("Телефон", max_length=32)
    email = models.EmailField("Email", blank=True)
    comment = models.TextField("Коментар", blank=True)

    # --- Доставка Нова Пошта (Фаза 0.5 — snapshot без API-звірки) ---
    city = models.CharField("Місто", max_length=120)
    np_type = models.CharField(
        "Тип отримання", max_length=16, choices=NovaPoshtaType.choices
    )
    np_point = models.CharField("Відділення / адреса", max_length=255)

    # --- Оплата ---
    payment_method = models.CharField(
        "Спосіб оплати", max_length=16, choices=PaymentMethod.choices, default=PaymentMethod.MONOBANK
    )
    payment_status = models.CharField(
        "Статус оплати", max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    monobank_invoice_id = models.CharField(
        "Monobank invoiceId", max_length=64, blank=True, db_index=True
    )

    status = models.CharField(
        "Статус замовлення", max_length=16, choices=OrderStatus.choices, default=OrderStatus.NEW
    )

    total_uah = models.DecimalField("Сума, UAH", max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField("Створено", auto_now_add=True)
    updated_at = models.DateTimeField("Оновлено", auto_now=True)

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"EMX-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def recalc_total(self) -> None:
        self.total_uah = sum((item.line_total for item in self.items.all()), start=0)


class OrderItem(models.Model):
    """Позиція замовлення. Усі товарні дані — snapshot на момент покупки (SEC-06)."""

    order = models.ForeignKey(Order, verbose_name="Замовлення", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "catalog.Product",
        verbose_name="Товар",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )

    product_sku = models.CharField("SKU (на момент замовлення)", max_length=32)
    product_name = models.CharField("Назва (на момент замовлення)", max_length=200)
    unit_price_uah = models.DecimalField("Ціна за од., UAH", max_digits=10, decimal_places=2)
    qty = models.PositiveSmallIntegerField("Кількість", default=1)

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"

    def __str__(self) -> str:
        return f"{self.product_name} × {self.qty}"

    @property
    def line_total(self):
        return self.unit_price_uah * self.qty
