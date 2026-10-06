"""Document <title>: бренд один раз на головній, суфікс на внутрішніх."""
import re

from django.test import TestCase
from django.urls import reverse

from core.seo import SITE_BRAND, with_brand_suffix


def _document_title(response) -> str:
    match = re.search(r"<title>(.*?)</title>", response.content.decode(), re.DOTALL)
    if match is None:
        raise AssertionError("у відповіді немає <title>")
    return match.group(1).strip()


class BrandSuffixHelperTests(TestCase):
    def test_skips_suffix_when_brand_already_in_title(self):
        title = with_brand_suffix("Euromaxi UA — зарядні станції в Україні")
        self.assertEqual(title.count(SITE_BRAND), 1)
        self.assertEqual(title, "Euromaxi UA — зарядні станції в Україні")

    def test_appends_suffix_when_brand_missing(self):
        self.assertEqual(with_brand_suffix("Контакти"), "Контакти — Euromaxi UA")


class DocumentTitleTests(TestCase):
    def test_home_title_contains_brand_once(self):
        response = self.client.get(reverse("core:home"))
        title = _document_title(response)
        self.assertEqual(title.count(SITE_BRAND), 1)
        self.assertEqual(title, "Euromaxi UA — зарядні станції в Україні")

    def test_inner_page_without_brand_gets_suffix(self):
        response = self.client.get(reverse("content:contacts"))
        title = _document_title(response)
        self.assertEqual(title, "Контакти — Euromaxi UA")
        self.assertEqual(title.count(SITE_BRAND), 1)
