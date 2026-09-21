"""Імпорт фото і PDF для 4 SKU SolarVault 3 з docs/euromaxi 4 items.

Ідемпотентна: наявні фото/документи пропускає (без --force).
"""
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from catalog.models import Product, ProductDocument, ProductDocumentKind, ProductImage

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
DOCS_ROOT = BASE_DIR / "docs" / "euromaxi 4 items"

# SKU -> (папка, впорядковані відносні шляхи фото)
PHOTOS: dict[str, tuple[str, list[str]]] = {
    "EMX-JACKERY-SV3-PRO": (
        "SolarVault 3 Pro/pics",
        [
            "主机_正视图.png",
            "主包_透视图右 拷贝.png",
            "主包_透视图左 拷贝.png",
            "主机_右视图.png",
            "主机_左视图.png",
            "主机_后视图.png",
        ],
    ),
    "EMX-JACKERY-SV3-PROMAX": (
        "2026_09_08_SolarVault 3 Pro Max MSDS/pics",
        ["1.png", "2.png", "3.png", "4.png", "5.png"],
    ),
    "EMX-JACKERY-SV3-PROMAXAC": (
        "2026_09_08_SolarVault 3 Pro Max AC MSDS/pics",
        [
            "S3ProMax-AC+S3BP2500.png",
            "S3ProMax-AC+S3BP2500+S3Base.png",
            "S3ProMax-AC + S3BP2500x2.png",
            "S3ProMax-AC + S3BP2500x3.png",
            "S3ProMax-AC + P1读表器.png",
            "TIC读表器+S3ProMax-AC.png",
        ],
    ),
    "EMX-JACKERY-SV3-BP2500": (
        "2026_09_08_SolarVault 3 BP2500 UN38.3 Test Report/pics",
        [
            "加电包_正视图 拷贝.png",
            "加电包_透视图右 拷贝.png",
            "加电包_透视图左 拷贝.png",
            "加电包_六视图 拷贝.png",
        ],
    ),
}

PDF_DIRS: dict[str, str] = {
    "EMX-JACKERY-SV3-PRO": "SolarVault 3 Pro",
    "EMX-JACKERY-SV3-PROMAX": "2026_09_08_SolarVault 3 Pro Max MSDS",
    "EMX-JACKERY-SV3-PROMAXAC": "2026_09_08_SolarVault 3 Pro Max AC MSDS",
    "EMX-JACKERY-SV3-BP2500": "2026_09_08_SolarVault 3 BP2500 UN38.3 Test Report",
}

SOLARVAULT_SKUS = frozenset(PHOTOS)


def _pdf_title(stem: str) -> str:
    low = stem.lower()
    if "msds" in low:
        return "MSDS"
    if "un38" in low or "un 38" in low:
        return "UN38.3 Test Report"
    if "doc" in low:
        return "EU Declaration of Conformity"
    if "ce-red" in low:
        return "CE-RED"
    if "red-4348" in low:
        return "EU Type Examination Certificate (RED)"
    if "voc" in low:
        return "VOC RED"
    return stem.replace("_", " ")[:200]


class Command(BaseCommand):
    help = "Імпорт фото та PDF сертифікатів SolarVault 3 з docs/euromaxi 4 items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Перезаписати фото і документи SolarVault.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        photos_n, docs_n, skipped = 0, 0, 0
        for sku in PHOTOS:
            product = Product.objects.filter(sku=sku).select_related("brand").first()
            if product is None:
                self.stderr.write(f"Немає товару {sku} — спочатку seed_catalog.")
                continue
            photos_n += self._import_photos(product, force)
            docs_n += self._import_pdfs(product, force)
            if not force and product.images.exists() and product.documents.exists():
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f"SolarVault: +{photos_n} фото, +{docs_n} PDF."
        ))

    def _import_photos(self, product: Product, force: bool) -> int:
        if product.images.exists() and not force:
            return 0
        if force:
            product.images.all().delete()
        rel_dir, names = PHOTOS[product.sku]
        added = 0
        for order, name in enumerate(names):
            path = DOCS_ROOT / rel_dir / name
            if not path.is_file():
                self.stderr.write(f"Немає фото {path}")
                continue
            image = ProductImage(
                product=product,
                alt=f"{product.brand.name} {product.name} — фото {order + 1}",
                order=order,
                is_primary=(order == 0),
                is_placeholder=False,
            )
            image.image.save(
                f"{product.sku}-{order + 1}{path.suffix.lower()}",
                ContentFile(path.read_bytes()),
                save=False,
            )
            image.save()
            added += 1
        return added

    def _import_pdfs(self, product: Product, force: bool) -> int:
        if product.documents.exists() and not force:
            return 0
        if force:
            for doc in product.documents.all():
                doc.file.delete(save=False)
            product.documents.all().delete()
        pdf_dir = DOCS_ROOT / PDF_DIRS[product.sku]
        added = 0
        for order, path in enumerate(sorted(pdf_dir.glob("*.pdf"))):
            title = _pdf_title(path.stem)
            doc = ProductDocument(
                product=product,
                kind=ProductDocumentKind.CERTIFICATE,
                title=title,
                order=order,
            )
            ascii_name = f"{product.sku}-{order + 1}.pdf"
            doc.file.save(ascii_name, ContentFile(path.read_bytes()), save=False)
            doc.save()
            added += 1
        return added
