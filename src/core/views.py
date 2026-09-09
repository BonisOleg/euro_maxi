from django.views.generic import ListView, TemplateView

from catalog.models import Brand, Product


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Euromaxi UA — зарядні станції в Україні"
        ctx["meta_description"] = (
            "Портативні та домашні зарядні станції Jackery, Bluetti, Anker з доставкою "
            "по Україні Новою Поштою. Оплата Monobank."
        )
        active_products = Product.objects.filter(is_active=True).select_related("brand")
        ctx["hit_products"] = active_products.filter(is_hit=True).prefetch_related("images")[:8]
        # Хіт+новинка — лише в «Хітах», щоб картка не дублювалась на головній.
        ctx["new_products"] = (
            active_products.filter(is_new=True, is_hit=False).prefetch_related("images")[:8]
        )

        brand_tiles = []
        for brand in Brand.objects.filter(products__is_active=True).distinct():
            sample = (
                Product.objects.filter(is_active=True, brand=brand)
                .prefetch_related("images")
                .first()
            )
            brand_tiles.append({"brand": brand, "image": sample.primary_image if sample else None})
        ctx["brand_tiles"] = brand_tiles
        return ctx


class SearchView(ListView):
    model = Product
    template_name = "core/search.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("brand").prefetch_related(
            "images"
        )
        query = self.request.GET.get("q", "").strip()
        if query:
            from django.db.models import Q

            qs = qs.filter(
                Q(name__icontains=query)
                | Q(brand__name__icontains=query)
                | Q(sku__icontains=query)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "").strip()
        ctx["page_title"] = f"Пошук: {ctx['query']}" if ctx["query"] else "Пошук"
        return ctx
