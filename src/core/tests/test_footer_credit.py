"""Кредит PrometeyLabs у футері: лінк лише на homepage, nofollow."""
from django.test import TestCase
from django.urls import reverse

from content.models import Page

CREDIT_URL = "https://www.prometeylabs.com/internet-shop-v2/"


class FooterDeveloperLinkTests(TestCase):
    def test_home_has_nofollow_credit_link(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, CREDIT_URL)
        self.assertContains(response, "nofollow")
        self.assertContains(response, ">PrometeyLabs</a>")
        self.assertContains(response, "Сайт розроблено в")

    def test_inner_pages_show_credit_without_link(self):
        Page.objects.create(
            title="Політика",
            slug="privacy",
            body="<p>x</p>",
            is_published=True,
        )
        urls = (
            reverse("content:contacts"),
            reverse("content:page_detail", kwargs={"slug": "privacy"}),
            reverse("catalog:product_list"),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, "PrometeyLabs")
                self.assertNotContains(response, CREDIT_URL)
                self.assertNotContains(response, "site-footer__credit-link")
