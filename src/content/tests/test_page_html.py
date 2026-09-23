from django.test import TestCase
from django.urls import reverse

from content.models import Page
from content.sanitize import clean_page_html


class PageHtmlSanitizeTests(TestCase):
    def test_strips_script_and_handlers(self):
        cleaned = clean_page_html(
            '<p onclick="alert(1)">Текст</p><script>alert(1)</script>'
            '<a href="javascript:alert(1)">лінк</a>'
            '<a href="/contacts/">контакти</a>'
            '<a href="mailto:info@euromaxi.ua">пошта</a>'
        )
        self.assertNotIn("script", cleaned.lower())
        self.assertNotIn("onclick", cleaned)
        self.assertNotIn("javascript:", cleaned)
        self.assertIn("<p>Текст</p>", cleaned)
        self.assertIn('href="/contacts/"', cleaned)
        self.assertIn('href="mailto:info@euromaxi.ua"', cleaned)

    def test_save_persists_cleaned_body(self):
        page = Page.objects.create(
            title="Про нас",
            slug="about",
            body="<h2>Хто ми</h2><script>alert(1)</script><p>Текст</p>",
        )
        page.refresh_from_db()
        self.assertIn("<h2>Хто ми</h2>", page.body)
        self.assertNotIn("script", page.body.lower())

    def test_page_view_does_not_render_script(self):
        Page.objects.create(
            title="Оферта",
            slug="offer",
            body="<p>Умови</p><img src=x onerror=alert(1)>",
            is_published=True,
        )
        response = self.client.get(reverse("content:page_detail", kwargs={"slug": "offer"}))
        self.assertContains(response, "<p>Умови</p>")
        self.assertNotContains(response, "onerror")
        self.assertNotContains(response, "<img")
