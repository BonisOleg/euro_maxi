"""Тести WebP-конвертації та валідації ImageField каталогу."""
import tempfile
from io import BytesIO
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from catalog.models import Brand, Product, ProductImage
from core.utils.images import validate_image


def _make_png(width: int = 100, height: int = 80, color=(200, 100, 50)) -> SimpleUploadedFile:
    buf = BytesIO()
    Image.new("RGB", (width, height), color).save(buf, format="PNG")
    return SimpleUploadedFile("test-photo.png", buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="chargua-webp-"))
class ValidateImageTests(TestCase):
    def test_rejects_bad_extension(self):
        f = SimpleUploadedFile("shell.php", b"<?php", content_type="application/x-php")
        with self.assertRaises(ValidationError):
            validate_image(f)

    def test_accepts_png(self):
        validate_image(_make_png())


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="chargua-webp-"))
class WebpConvertOnSaveTests(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="Test Brand")
        self.product = Product.objects.create(
            brand=self.brand,
            sku="EMX-TEST-WEBP",
            name="Test Product",
        )

    def test_product_image_becomes_webp(self):
        img = ProductImage.objects.create(
            product=self.product,
            image=_make_png(400, 300),
            is_primary=True,
        )
        img.refresh_from_db()
        self.assertTrue(img.image.name.lower().endswith(".webp"))
        with Image.open(img.image.path) as opened:
            self.assertEqual(opened.format, "WEBP")
            self.assertEqual(opened.size, (400, 300))

    def test_oversized_resized(self):
        img = ProductImage.objects.create(
            product=self.product,
            image=_make_png(2000, 1500),
        )
        img.refresh_from_db()
        with Image.open(img.image.path) as opened:
            self.assertEqual(opened.format, "WEBP")
            self.assertLessEqual(max(opened.size), 1200)

    def test_brand_logo_stays_original(self):
        self.brand.logo = _make_png(320, 240)
        self.brand.save()
        self.brand.refresh_from_db()
        self.assertTrue(self.brand.logo.name.lower().endswith(".png"))
        self.assertFalse(self.brand.logo.name.lower().endswith(".webp"))
        with Image.open(self.brand.logo.path) as opened:
            self.assertEqual(opened.format, "PNG")
            self.assertEqual(opened.size, (320, 240))

    def test_small_webp_not_reprocessed(self):
        buf = BytesIO()
        Image.new("RGB", (200, 160), (10, 20, 30)).save(buf, format="WEBP")
        upload = SimpleUploadedFile("already.webp", buf.getvalue(), content_type="image/webp")
        img = ProductImage.objects.create(product=self.product, image=upload)
        img.refresh_from_db()
        self.assertTrue(Path(img.image.name).name.startswith("already"))
        self.assertTrue(img.image.name.lower().endswith(".webp"))
