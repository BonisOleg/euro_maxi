from pathlib import Path

from django.db.models import Case, IntegerField, Prefetch, Q, Value, When
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.text import get_valid_filename
from django.views.generic import DetailView, ListView

from .models import BatteryType, Brand, Product, ProductDocument, ProductDocumentKind

SORT_OPTIONS = {
    "price_asc": "price_uah",
    "price_desc": "-price_uah",
    "power_desc": "-output_power_w",
    "capacity_desc": "-capacity_wh",
}

# Діапазони: OR всередині групи, AND між групами.
# Ключі БЕЗ «+» — у application/x-www-form-urlencoded «+» стає пробілом,
# тож value="1501+" прилітає як "1501 " і фільтр мовчки відпадає (порожній Q() = усі).
POWER_RANGES = {
    "0-500": (None, 500),
    "501-1500": (501, 1500),
    "1501up": (1501, None),
}
CAPACITY_RANGES = {
    "0-500": (None, 500),
    "501-1000": (501, 1000),
    "1001up": (1001, None),
}

# Старі значення з макета / закладок (після + → пробіл у GET).
_RANGE_ALIASES = {
    "1501+": "1501up",
    "1501 ": "1501up",
    "1501": "1501up",
    "1001+": "1001up",
    "1001 ": "1001up",
    "1001": "1001up",
}


def _normalize_range_values(values: list[str]) -> list[str]:
    out = []
    for raw in values:
        key = _RANGE_ALIASES.get(raw, _RANGE_ALIASES.get(raw.strip(), raw.strip()))
        out.append(key)
    return out


def _range_q(field: str, values: list[str], ranges: dict) -> Q | None:
    """Повертає Q для OR-діапазонів або None, якщо жоден ключ не валідний.

    None — сигнал «не застосовувати фільтр» (на відміну від порожнього Q(),
    який у Django означає «усі рядки»).
    """
    q = Q()
    matched = False
    for value in _normalize_range_values(values):
        bounds = ranges.get(value)
        if not bounds:
            continue
        lo, hi = bounds
        cond = Q()
        if lo is not None:
            cond &= Q(**{f"{field}__gte": lo})
        if hi is not None:
            cond &= Q(**{f"{field}__lte": hi})
        q |= cond
        matched = True
    return q if matched else None


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("brand").prefetch_related(
            "images"
        )

        brand_slugs = self.request.GET.getlist("brand")
        if brand_slugs:
            qs = qs.filter(brand__slug__in=brand_slugs)

        battery_types = self.request.GET.getlist("battery")
        if battery_types:
            qs = qs.filter(battery_type__in=battery_types)

        power_ranges = self.request.GET.getlist("power")
        if power_ranges:
            power_q = _range_q("output_power_w", power_ranges, POWER_RANGES)
            if power_q is not None:
                qs = qs.filter(power_q)

        capacity_ranges = self.request.GET.getlist("capacity")
        if capacity_ranges:
            capacity_q = _range_q("capacity_wh", capacity_ranges, CAPACITY_RANGES)
            if capacity_q is not None:
                qs = qs.filter(capacity_q)

        sort = self.request.GET.get("sort")
        order_field = SORT_OPTIONS.get(sort)
        qs = qs.order_by(order_field) if order_field else qs

        return qs.distinct()

    def get_template_names(self):
        if self.request.htmx:
            return ["catalog/_product_grid.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Каталог зарядних станцій"
        ctx["meta_description"] = (
            "Портативні зарядні станції Jackery, Bluetti, Anker — ціни в гривнях, "
            "доставка Новою Поштою."
        )
        ctx["brands"] = Brand.objects.filter(products__is_active=True).distinct()
        ctx["battery_choices"] = BatteryType.choices
        ctx["power_ranges"] = [
            ("0-500", "до 500 Вт"),
            ("501-1500", "501–1500 Вт"),
            ("1501up", "від 1501 Вт"),
        ]
        ctx["capacity_ranges"] = [
            ("0-500", "до 500 Вт·год"),
            ("501-1000", "501–1000 Вт·год"),
            ("1001up", "від 1001 Вт·год"),
        ]
        ctx["selected_brands"] = self.request.GET.getlist("brand")
        ctx["selected_battery"] = self.request.GET.getlist("battery")
        # Нормалізуємо для checked-стану чекбоксів після GET з «+»/пробілом.
        ctx["selected_power"] = _normalize_range_values(self.request.GET.getlist("power"))
        ctx["selected_capacity"] = _normalize_range_values(self.request.GET.getlist("capacity"))
        ctx["selected_sort"] = self.request.GET.get("sort", "")
        params = self.request.GET.copy()
        params.pop("page", None)
        if not params.get("sort"):
            params.pop("sort", None)
        ctx["querystring"] = params.urlencode()
        return ctx


def _documents_for_pdp():
    """Інструкції першими, далі сертифікати; у групі — order."""
    return ProductDocument.objects.order_by(
        Case(
            When(kind=ProductDocumentKind.MANUAL, then=Value(0)),
            When(kind=ProductDocumentKind.CERTIFICATE, then=Value(1)),
            default=Value(9),
            output_field=IntegerField(),
        ),
        "order",
        "id",
    )


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("brand").prefetch_related(
            "images",
            Prefetch("documents", queryset=_documents_for_pdp()),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = self.object.name
        ctx["meta_description"] = self.object.short_description
        ctx["related_products"] = (
            Product.objects.filter(is_active=True, brand=self.object.brand)
            .exclude(pk=self.object.pk)
            .select_related("brand")
            .prefetch_related("images")[:4]
        )
        return ctx


def product_document_download(request, slug: str, pk: int) -> FileResponse:
    """Скачування PDF з Content-Disposition: attachment (iOS Safari)."""
    doc = get_object_or_404(
        ProductDocument.objects.select_related("product"),
        pk=pk,
        product__slug=slug,
        product__is_active=True,
    )
    if not doc.file:
        raise Http404
    filename = get_valid_filename(Path(doc.file.name).name)
    if not filename.lower().endswith(".pdf"):
        filename = f"{filename}.pdf"
    return FileResponse(
        doc.file.open("rb"),
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )
