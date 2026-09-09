"""Масовий перерахунок роздрібних цін UAH з закупівельної EUR netto.

Курс і націнку клієнт підтверджує окремо (немає в Excel/ТЗ) — команда ніколи
не хардкодить ці числа, вони лише параметри запуску.

SEC-09: floor-price захист — ціна ніколи не опускається нижче
`price_eur_netto * rate` (собівартість без націнки), навіть при округленні.

За замовчуванням команда лише рахує і показує ціни (dry-run за духом):
`is_price_confirmed`/`is_active` не змінюються, доки не передано --activate —
це свідоме рішення (SEC-02: без ручного підтвердження товар не продається).
"""
from decimal import ROUND_CEILING, Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Product


def _round_up(value: Decimal, step: int) -> Decimal:
    """Округлює вгору до кратного `step` грн (напр. 1234.5 → 1240 при step=10)."""
    if step <= 0:
        return value.quantize(Decimal("1"), rounding=ROUND_CEILING)
    step_d = Decimal(step)
    return (value / step_d).to_integral_value(rounding=ROUND_CEILING) * step_d


class Command(BaseCommand):
    help = (
        "Перерахунок price_uah з price_eur_netto за курсом і націнкою. "
        "SEC-09: floor-price — ціна не нижче собівартості в UAH."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--rate", type=Decimal, required=True, help="Курс EUR/UAH, напр. 47.5"
        )
        parser.add_argument(
            "--markup", type=Decimal, required=True, help="Націнка у %%, напр. 35"
        )
        parser.add_argument(
            "--round-to",
            type=int,
            default=10,
            help="Округлення ціни вгору до кратного N грн (default 10, 0 = без округлення)",
        )
        parser.add_argument(
            "--sku", nargs="*", default=None, help="Обмежити перерахунок конкретними SKU"
        )
        parser.add_argument(
            "--activate",
            action="store_true",
            help=(
                "Одразу виставити is_price_confirmed=True та is_active=True. "
                "Без цього флагу команда лише рахує ціну — активація вручну в адмінці."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показати результат без збереження в БД",
        )

    def handle(self, *args, **options):
        rate: Decimal = options["rate"]
        markup_pct: Decimal = options["markup"]
        round_to: int = options["round_to"]

        if rate <= 0:
            raise CommandError("--rate має бути більше 0.")
        if markup_pct < 0:
            raise CommandError("--markup не може бути від'ємним (продаж нижче собівартості).")

        qs = Product.objects.filter(price_eur_netto__isnull=False).select_related("brand")
        if options["sku"]:
            qs = qs.filter(sku__in=options["sku"])
        qs = qs.order_by("brand__name", "name")

        if not qs.exists():
            self.stdout.write(self.style.WARNING("Немає товарів з price_eur_netto для перерахунку."))
            return

        multiplier = 1 + markup_pct / Decimal("100")
        rows = []
        for product in qs:
            floor_price = (product.price_eur_netto * rate).quantize(Decimal("1"))
            raw_price = product.price_eur_netto * rate * multiplier
            price_uah = _round_up(raw_price, round_to)
            if price_uah < floor_price:
                # SEC-09: не повинно статись при markup >= 0, але про всяк випадок
                # захищаємось від продажу нижче собівартості через округлення вниз.
                price_uah = floor_price
            rows.append((product, price_uah, floor_price))

        self.stdout.write(
            f"{'SKU':<26} {'Бренд':<9} {'Назва':<32} {'netto €':>9} {'floor UAH':>10} {'→ ціна UAH':>11}"
        )
        for product, price_uah, floor_price in rows:
            self.stdout.write(
                f"{product.sku:<26} {product.brand.name:<9} {product.name[:32]:<32} "
                f"{product.price_eur_netto:>9} {floor_price:>10} {price_uah:>11}"
            )

        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(f"\nDRY-RUN: {len(rows)} товарів прораховано, нічого не збережено.")
            )
            return

        with transaction.atomic():
            for product, price_uah, _floor in rows:
                product.price_uah = price_uah
                if options["activate"]:
                    product.is_price_confirmed = True
                    product.is_active = True
                product.save(update_fields=["price_uah", "is_price_confirmed", "is_active", "updated_at"])

        if options["activate"]:
            note = "Товари активовано (is_active=True, is_price_confirmed=True)."
        else:
            note = (
                "Товари НЕ активовано — перевірте ціни в адмінці й вручну виставте "
                "is_price_confirmed + is_active (SEC-02), або перезапустіть з --activate."
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"\nОновлено price_uah для {len(rows)} товарів "
                f"(курс {rate} EUR/UAH, націнка {markup_pct}%). {note}"
            )
        )
