"""Одноразовий імпорт фото каталогу.

- 5 підтверджених Jackery (500V2/1000V2/1000Plus/2000V2/3000V2) — реальні фото
  з `photo/<модель>/02_Оброблені_БЕС/` (клієнт завантажив у workspace).
- Решта 16 SKU (5 інших Jackery + 8 Bluetti + 3 Anker) — фото немає, генерується
  візуальна заглушка (бренд + модель на нейтральному фоні бренд-кольорів сайту),
  is_placeholder=True — легко знайти в адмінці й замінити, коли клієнт надасть фото.

Ідемпотентна: якщо у товару вже є фото — пропускає (без --force).
"""
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from catalog.models import Product, ProductImage

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
PHOTO_ROOT = BASE_DIR / "photo"

# SKU -> назва папки в photo/ (реальні фото від клієнта)
SOLARVAULT_SKUS = {
    "EMX-JACKERY-SV3-PRO",
    "EMX-JACKERY-SV3-PROMAX",
    "EMX-JACKERY-SV3-PROMAXAC",
    "EMX-JACKERY-SV3-BP2500",
}

SKU_TO_PHOTO_DIR = {
    "EMX-JACKERY-500V2": "JACK-PS-500-V2",
    "EMX-JACKERY-1000V2": "JACK-PS-1000-V2",
    "EMX-JACKERY-1000PLUS": "JACK-PS-1000-PLUS",
    "EMX-JACKERY-2000V2": "JACK-PS-2000-V2",
    "EMX-JACKERY-3000V2": "JACK-PS-3000-V2",
}

PLACEHOLDER_BG = (238, 244, 249)  # --color-bg-muted
PLACEHOLDER_BORDER = (168, 197, 219)  # --color-border-strong
PLACEHOLDER_TEXT = (10, 77, 122)  # --color-text
PLACEHOLDER_ACCENT = (0, 115, 184)  # --color-primary

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _make_placeholder_bytes(brand: str, name: str) -> bytes:
    width, height = 800, 800
    img = Image.new("RGB", (width, height), PLACEHOLDER_BG)
    draw = ImageDraw.Draw(img)

    margin = 24
    draw.rectangle(
        [margin, margin, width - margin, height - margin],
        outline=PLACEHOLDER_BORDER,
        width=3,
    )

    # Стилізована іконка блискавки (bolt) по центру
    cx, cy = width // 2, height // 2 - 60
    bolt = [
        (cx - 30, cy - 90), (cx + 20, cy - 90), (cx - 10, cy - 10),
        (cx + 35, cy - 10), (cx - 25, cy + 100), (cx - 5, cy + 5),
        (cx - 45, cy + 5),
    ]
    draw.polygon(bolt, fill=PLACEHOLDER_ACCENT)

    font_brand = _load_font(40)
    font_name = _load_font(28)
    font_note = _load_font(20)

    def centered_text(y: int, text: str, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        draw.text((width / 2 - w / 2, y), text, font=font, fill=fill)

    centered_text(height / 2 + 60, brand, font_brand, PLACEHOLDER_TEXT)
    centered_text(height / 2 + 115, name, font_name, PLACEHOLDER_TEXT)
    centered_text(height - 90, "Фото очікується", font_note, (90, 122, 148))

    from io import BytesIO

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


class Command(BaseCommand):
    help = "Імпорт реальних фото (5 Jackery) + генерація заглушок (решта 16 SKU)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Перезаписати фото навіть якщо у товару вже є ProductImage.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        real_count, placeholder_count, skipped = 0, 0, 0

        for product in Product.objects.select_related("brand").all():
            if product.sku in SOLARVAULT_SKUS:
                skipped += 1
                continue
            if product.images.exists() and not force:
                skipped += 1
                continue
            if force:
                product.images.all().delete()

            photo_dir_name = SKU_TO_PHOTO_DIR.get(product.sku)
            if photo_dir_name:
                real_count += self._import_real_photos(product, photo_dir_name)
            else:
                self._create_placeholder(product)
                placeholder_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Фото: {real_count} реальних додано, {placeholder_count} заглушок згенеровано, "
            f"{skipped} товарів пропущено (вже мають фото)."
        ))

    def _import_real_photos(self, product: Product, photo_dir_name: str) -> int:
        source_dir = PHOTO_ROOT / photo_dir_name / "02_Оброблені_БЕС"
        if not source_dir.is_dir():
            self.stderr.write(f"Немає папки {source_dir} для {product.sku} — створюю заглушку.")
            self._create_placeholder(product)
            return 0

        def priority(path: Path) -> tuple:
            stem = path.stem.lower()
            for rank, keyword in enumerate(("front", "angle-view", "flat-top", "portable-power-station")):
                if keyword in stem:
                    return (rank, stem)
            return (99, stem)

        files = sorted(
            (p for p in source_dir.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")),
            key=priority,
        )
        added = 0
        for order, file_path in enumerate(files[:6]):
            with open(file_path, "rb") as fh:
                content = ContentFile(fh.read())
            image = ProductImage(
                product=product,
                alt=f"{product.brand.name} {product.name} — фото {order + 1}",
                order=order,
                is_primary=(order == 0),
                is_placeholder=False,
            )
            image.image.save(f"{product.sku}-{order + 1}{file_path.suffix.lower()}", content, save=False)
            image.save()
            added += 1
        return added

    def _create_placeholder(self, product: Product) -> None:
        content = _make_placeholder_bytes(product.brand.name, product.name)
        image = ProductImage(
            product=product,
            alt=f"{product.brand.name} {product.name} — фото очікується",
            order=0,
            is_primary=True,
            is_placeholder=True,
        )
        image.image.save(f"{product.sku}-placeholder.jpg", ContentFile(content), save=False)
        image.save()
