from django.contrib import admin
from unfold.decorators import display
from unfold.admin import ModelAdmin, TabularInline

from .models import Order, OrderItem, OrderStatus, PaymentStatus


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    fields = ["product", "product_sku", "product_name", "unit_price_uah", "qty", "line_total"]
    readonly_fields = ["product_sku", "product_name", "unit_price_uah", "line_total"]

    @admin.display(description="Сума")
    def line_total(self, obj):
        return obj.line_total


_STATUS_LABELS = {
    OrderStatus.NEW: "info",
    OrderStatus.CONFIRMED: "primary",
    OrderStatus.SHIPPED: "warning",
    OrderStatus.DONE: "success",
    OrderStatus.CANCELLED: "danger",
}
_PAYMENT_LABELS = {
    PaymentStatus.PENDING: "warning",
    PaymentStatus.PAID: "success",
    PaymentStatus.FAILED: "danger",
}


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        "order_number",
        "full_name",
        "phone",
        "city",
        "total_uah",
        "status_badge",
        "payment_badge",
        "created_at",
    ]
    list_filter = ["status", "payment_status", "np_type", "created_at"]
    search_fields = ["order_number", "full_name", "phone", "email"]
    readonly_fields = ["order_number", "total_uah", "created_at", "updated_at", "monobank_invoice_id"]
    inlines = [OrderItemInline]

    @display(description="Статус", label=_STATUS_LABELS)
    def status_badge(self, obj):
        return obj.status

    @display(description="Оплата", label=_PAYMENT_LABELS)
    def payment_badge(self, obj):
        return obj.payment_status
