"""Пошук товарів: нормалізація, ранжування, підказки, збереження q."""
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from catalog.models import Brand, Product
from catalog.search import normalize_search_text


def _product(brand, sku, name, **kwargs):
    return Product.objects.create(
        brand=brand,
        sku=sku,
        name=name,
        slug=kwargs.pop("slug", sku.lower()),
        is_active=kwargs.pop("is_active", True),
        **kwargs,
    )


class NormalizeSearchTests(TestCase):
    def test_folds_cyrillic_quotes_and_spaces(self):
        self.assertEqual(normalize_search_text("  «Ікра»  ЄҐ  "), "икра ег")


class SearchViewTests(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="Jackery", slug="jackery")

    def test_quotes_and_case_find_product(self):
        _product(self.brand, "EMX-CHERRI", name='Насіння «Черрі»')
        for query in ("черрі", "ЧЕРРІ", "Черрі"):
            response = self.client.get(reverse("core:search"), {"q": query})
            self.assertContains(response, "EMX-CHERRI")

    def test_uk_fold_finds_i_and_yi(self):
        _product(self.brand, "EMX-IKRA", name="Ікра")
        response = self.client.get(reverse("core:search"), {"q": "икра"})
        self.assertContains(response, "EMX-IKRA")

    def test_brand_and_sku_and_word_order(self):
        _product(
            self.brand,
            "EMX-EX-1000",
            name="Explorer 1000",
            short_description="Портативна станція",
        )
        by_brand = self.client.get(reverse("core:search"), {"q": "jackery"})
        by_sku = self.client.get(reverse("core:search"), {"q": "emx-ex-1000"})
        by_words = self.client.get(reverse("core:search"), {"q": "1000 explorer"})
        self.assertContains(by_brand, "EMX-EX-1000")
        self.assertContains(by_sku, "EMX-EX-1000")
        self.assertContains(by_words, "EMX-EX-1000")

    def test_inactive_hidden(self):
        _product(self.brand, "EMX-OFF", name="Прихована станція", is_active=False)
        response = self.client.get(reverse("core:search"), {"q": "прихована"})
        self.assertNotContains(response, "EMX-OFF")

    def test_empty_query_does_not_list_catalog(self):
        _product(self.brand, "EMX-ALL", name="Видима станція")
        response = self.client.get(reverse("core:search"))
        self.assertContains(response, "Введіть запит")
        self.assertNotContains(response, 'data-add="EMX-ALL"')

    def test_exact_sku_ranks_above_description(self):
        _product(self.brand, "EMX-FIND", name="Точний артикул")
        _product(
            self.brand,
            "EMX-OTHER",
            name="Інший товар",
            description="Згадка артикула EMX-FIND у тексті",
        )
        response = self.client.get(reverse("core:search"), {"q": "EMX-FIND"})
        html = response.content.decode()
        self.assertLess(html.index('data-add="EMX-FIND"'), html.index('data-add="EMX-OTHER"'))

    def test_pagination_keeps_query(self):
        for index in range(13):
            _product(self.brand, f"EMX-P-{index:02d}", name=f"Станція {index}")
        response = self.client.get(reverse("core:search"), {"q": "станція", "page": "2"})
        self.assertContains(response, "page=1")
        self.assertContains(response, "q=")
        self.assertContains(response, "EMX-P-")

    def test_price_update_does_not_rebuild_index(self):
        product = _product(self.brand, "EMX-KEEP", name="Станція")
        Product.objects.filter(pk=product.pk).update(search_text="sentinel")
        product.is_hit = True
        product.save(update_fields=["is_hit"])
        product.refresh_from_db()
        self.assertEqual(product.search_text, "sentinel")

    def test_brand_rename_updates_index(self):
        product = _product(self.brand, "EMX-BR", name="Station")
        self.brand.name = "Bluetti"
        self.brand.save()
        product.refresh_from_db()
        self.assertIn("bluetti", product.search_text)
        self.assertNotIn("jackery", product.search_text)
        found = self.client.get(reverse("core:search"), {"q": "bluetti"})
        self.assertContains(found, "EMX-BR")


class SearchSuggestTests(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="Bluetti", slug="bluetti")

    def test_suggest_limits_to_eight(self):
        for index in range(9):
            _product(self.brand, f"EMX-SG-{index}", name=f"Портативна {index}")
        response = self.client.get(reverse("core:search_suggest"), {"q": "портативна"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode().count('role="option"'), 8)
        self.assertContains(response, "Показати всі результати")

    def test_suggest_short_query_is_empty(self):
        _product(self.brand, "EMX-SG", name="Портативна")
        response = self.client.get(reverse("core:search_suggest"), {"q": "п"})
        self.assertEqual(response.content.strip(), b"")


class RebuildSearchTextTests(TestCase):
    def test_command_restores_index(self):
        brand = Brand.objects.create(name="Anker", slug="anker")
        product = _product(brand, "EMX-RB", name="Сонячна панель")
        Product.objects.filter(pk=product.pk).update(search_text="", search_name="")
        call_command("rebuild_search_text")
        product.refresh_from_db()
        self.assertIn("сонячна", product.search_text)
        self.assertIn("anker", product.search_text)
