"""Тести PDF-документів товару (валідація + скачування)."""
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from catalog.models import Brand, Product, ProductDocument, ProductDocumentKind
from core.utils.documents import validate_pdf

MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n"


def _pdf_upload(name: str = "manual.pdf") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, MINIMAL_PDF, content_type="application/pdf")


class ValidatePdfTests(TestCase):
    def test_rejects_non_pdf_extension(self):
        f = SimpleUploadedFile("shell.php", b"<?php", content_type="application/x-php")
        with self.assertRaises(ValidationError):
            validate_pdf(f)

    def test_rejects_fake_pdf(self):
        f = SimpleUploadedFile("fake.pdf", b"not-a-pdf", content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_pdf(f)

    def test_accepts_pdf(self):
        validate_pdf(_pdf_upload())


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="chargua-docs-"))
class ProductDocumentTests(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="Doc Brand")
        self.product = Product.objects.create(
            brand=self.brand,
            sku="EMX-TEST-DOC",
            name="Doc Product",
            slug="doc-product",
            is_active=True,
            is_price_confirmed=True,
            price_uah="1000.00",
        )

    def test_title_from_filename(self):
        doc = ProductDocument.objects.create(
            product=self.product,
            kind=ProductDocumentKind.MANUAL,
            file=_pdf_upload("user_manual_ua.pdf"),
        )
        self.assertEqual(doc.title, "user manual ua")

    def test_download_attachment(self):
        doc = ProductDocument.objects.create(
            product=self.product,
            kind=ProductDocumentKind.CERTIFICATE,
            title="CE",
            file=_pdf_upload("ce.pdf"),
        )
        url = reverse("catalog:document_download", args=[self.product.slug, doc.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response.get("Content-Disposition", ""))
        self.assertIn("ce.pdf", response.get("Content-Disposition", ""))

    def test_download_hidden_for_inactive(self):
        self.product.is_active = False
        self.product.save(update_fields=["is_active"])
        doc = ProductDocument.objects.create(
            product=self.product,
            kind=ProductDocumentKind.MANUAL,
            file=_pdf_upload(),
        )
        url = reverse("catalog:document_download", args=[self.product.slug, doc.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_pdp_lists_documents(self):
        ProductDocument.objects.create(
            product=self.product,
            kind=ProductDocumentKind.MANUAL,
            title="Інструкція UA",
            file=_pdf_upload("instr.pdf"),
        )
        url = reverse("catalog:product_detail", args=[self.product.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Документи")
        self.assertContains(response, "Інструкція UA")
        self.assertContains(response, "Відкрити")
        self.assertContains(response, "Скачати")
