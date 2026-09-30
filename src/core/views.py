from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, TemplateView

from catalog.models import Brand, Product
from catalog.search import SUGGEST_LIMIT, apply_search, search_tokens, suggest_is_limited


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
        query = self.request.GET.get("q", "")
        qs = apply_search(qs, query)
        return qs.order_by("rank", "-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        ctx["query"] = query
        ctx["search_too_short"] = not search_tokens(query)
        ctx["page_title"] = f"Пошук: {query}" if query else "Пошук"
        return ctx


class SearchSuggestView(View):
    def get(self, request):
        if suggest_is_limited(request):
            return HttpResponse(status=429)
        query = request.GET.get("q", "")
        searchable = bool(search_tokens(query))
        products = []
        if searchable:
            qs = apply_search(
                Product.objects.filter(is_active=True).select_related("brand"),
                query,
            )
            products = list(
                qs.order_by("rank", "-created_at").prefetch_related("images")[:SUGGEST_LIMIT]
            )
        return render(
            request,
            "core/_search_suggest.html",
            {"products": products, "query": query, "searchable": searchable},
        )
