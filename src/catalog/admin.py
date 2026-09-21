from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Brand, Product, ProductDocument, ProductImage


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ["name", "slug", "product_count"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}

    @admin.display(description="Товарів")
    def product_count(self, obj):
        return obj.products.count()


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "alt", "order", "is_primary", "is_placeholder"]


class ProductDocumentInline(TabularInline):
    model = ProductDocument
    extra = 1
    fields = ["kind", "title", "file", "order"]


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = [
        "sku",
        "brand",
        "name",
        "price_uah",
        "is_active",
        "is_price_confirmed",
        "is_specs_confirmed",
        "is_hit",
        "is_new",
    ]
    list_filter = ["brand", "battery_type", "is_active", "is_price_confirmed", "is_hit", "is_new"]
    search_fields = ["sku", "name", "brand__name"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [ProductImageInline, ProductDocumentInline]
    autocomplete_fields = ["brand"]

    fieldsets = (
        ("Основне", {"fields": ("brand", "sku", "name", "slug")}),
        (
            "Характеристики",
            {
                "fields": (
                    "capacity_wh",
                    "output_power_w",
                    "battery_type",
                    "outputs",
                    "charging",
                    "features",
                    "weight_kg",
                    "dimensions",
                )
            },
        ),
        ("Опис", {"fields": ("short_description", "description")}),
        (
            "Ціна",
            {
                "fields": (
                    "price_eur_netto",
                    "price_uah",
                    "old_price_uah",
                    "is_price_confirmed",
                )
            },
        ),
        (
            "Публікація",
            {"fields": ("is_active", "is_hit", "is_new", "is_specs_confirmed")},
        ),
    )
