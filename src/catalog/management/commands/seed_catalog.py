"""Одноразовий seed каталогу — 21 SKU (Jackery + Bluetti + Anker-draft).

Дані звірені з:
- docs/01_MASTER_CATALOG_LightEnergyBase_Eurmaxi.xlsx (5 підтверджених Jackery: ціна netto, брутто-вага)
- docs/Ukr file 1.xlsx (усі 21: Battery Type/Rated Power з опису постачальника, ціна netto, вага)
- lightenergybase.com — офіційні картки для 5 підтверджених Jackery (ємність Вт·год, розʼєми,
  час зарядки, функції, вага/габарити пристрою) — саме тому лише вони is_specs_confirmed=True.

Ціна UAH навмисно НЕ рахується тут (немає підтвердженого курсу/націнки від клієнта) —
усі товари створюються з price_uah=None, is_active=False. Команда ідемпотентна
(update_or_create за sku) — повторний запуск не створює дублів.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import BatteryType, Brand, Product

# battery_type у Excel — довільний текст постачальника, мапимо на choices моделі
BATTERY_MAP = {
    "LiFePO4": BatteryType.LIFEPO4,
    "Lithium-ion (NCM)": BatteryType.LI_ION,
}

# --- 5 підтверджених Jackery (lightenergybase.com — повні специфікації) ---
JACKERY_MASTER = [
    dict(
        sku="EMX-JACKERY-500V2", name="Explorer 500 V2",
        price_eur_netto="204.00", weight_kg="6.10", dimensions="255×185×180",
        battery_type=BatteryType.LIFEPO4, output_power_w=500, capacity_wh=512,
        outputs="2× Schuko (EU) 230В (чиста синусоїда), 1× USB-C PD 100Вт, 1× USB-A, 12В авто-вихід",
        charging="Заряджання від мережі 220В: 0–100% за 60 хв",
        features="Вбудований LED-ліхтар; BMS ChargeShield 2.0; ресурс 6000+ циклів заряджання",
        is_specs_confirmed=True,
    ),
    dict(
        sku="EMX-JACKERY-1000V2", name="Explorer 1000 V2",
        price_eur_netto="340.00", weight_kg="10.80", dimensions="327×224×247",
        battery_type=BatteryType.LIFEPO4, output_power_w=1500, capacity_wh=1070,
        outputs="2× Schuko (EU) 230В, 2× USB-C PD 100Вт, 1× USB-A, 12В авто-вихід",
        charging="Заряджання від мережі: 0–100% за 60 хв; перемикання ДБЖ < 10мс",
        features="Керування через Jackery App (Wi-Fi/Bluetooth); ресурс 4000+ циклів; ручка Flat-Top",
        is_specs_confirmed=True,
    ),
    dict(
        sku="EMX-JACKERY-1000PLUS", name="Explorer 1000 Plus",
        price_eur_netto="433.00", weight_kg="14.50", dimensions="356×260×283",
        battery_type=BatteryType.LIFEPO4, output_power_w=2000, capacity_wh=1264,
        outputs="2× Schuko (EU) 230В, 2× USB-C PD 100Вт, 2× USB-A, 12В авто-вихід",
        charging="Заряджання від мережі: 0–100% за 1,7 год; перемикання ДБЖ < 10мс",
        features="Модульне розширення ємності до 5 кВт·год додатковими батареями; ресурс 4000+ циклів",
        is_specs_confirmed=True,
    ),
    dict(
        sku="EMX-JACKERY-2000V2", name="Explorer 2000 V2",
        price_eur_netto="588.00", weight_kg="18.00", dimensions="396×280×275",
        battery_type=BatteryType.LIFEPO4, output_power_w=2200, capacity_wh=2042,
        outputs="2× Schuko (EU) 230В, 2× USB-C PD 100Вт, 1× USB-A, 12В авто-вихід",
        charging="Заряджання від мережі: 0–100% за 1,6 год; перемикання ДБЖ < 10мс",
        features="Керування через Jackery App; ресурс 4000+ циклів; охолодження тихіше на 30%",
        is_specs_confirmed=True,
    ),
    dict(
        sku="EMX-JACKERY-3000V2", name="Explorer 3000 V2",
        price_eur_netto="1052.00", weight_kg="28.60", dimensions="473×359×373",
        battery_type=BatteryType.LIFEPO4, output_power_w=3000, capacity_wh=3276,
        outputs="3× Schuko (EU) 230В, 2× USB-C PD 100Вт, 2× USB-A, 12В авто-вихід, промисловий супер-вихід",
        charging="Заряджання від мережі: 0–100% за 1,8 год; перемикання ДБЖ < 10мс",
        features="Сертифікація ударостійкості корпусу IEC 60068-3; ресурс 4000+ циклів",
        is_specs_confirmed=True,
    ),
]

# --- 5 інших Jackery (Ukr file 1.xlsx — лише battery/power/вага підтверджені постачальником) ---
JACKERY_DRAFT = [
    dict(
        sku="EMX-JACKERY-100PLUS", name="Explorer 100 Plus EU",
        price_eur_netto="55.00", weight_kg="1.19", dimensions="",
        battery_type=BatteryType.LIFEPO4, output_power_w=128,
    ),
    dict(
        sku="EMX-JACKERY-240V2", name="Explorer 240 V2 EU",
        price_eur_netto="154.00", weight_kg="5.07", dimensions="288×198×268",
        battery_type=BatteryType.LIFEPO4, output_power_w=300,
    ),
    dict(
        sku="EMX-JACKERY-300D", name="Explorer 300D EU",
        price_eur_netto="119.00", weight_kg="2.88", dimensions="",
        battery_type=BatteryType.LIFEPO4, output_power_w=300,
    ),
    dict(
        sku="EMX-JACKERY-2000PLUS", name="Explorer 2000 Plus EU",
        price_eur_netto="805.00", weight_kg="27.90", dimensions="",
        battery_type=BatteryType.LIFEPO4, output_power_w=3000,
    ),
    dict(
        sku="EMX-JACKERY-3000PRO", name="Explorer 3000 Pro EU",
        price_eur_netto="929.00", weight_kg="33.00", dimensions="",
        battery_type=BatteryType.LI_ION, output_power_w=3000,
    ),
]

# --- 8 Bluetti (Ukr file 1.xlsx — без фото від клієнта) ---
BLUETTI = [
    dict(sku="EMX-BLUETTI-AC50P", name="AC50P", price_eur_netto="204.00",
         weight_kg="6.80", battery_type=BatteryType.LIFEPO4, output_power_w=700),
    dict(sku="EMX-BLUETTI-AC70P", name="AC70P", price_eur_netto="305.00",
         weight_kg="10.20", battery_type=BatteryType.LIFEPO4, output_power_w=1000),
    dict(sku="EMX-BLUETTI-AC180P", name="AC180P", price_eur_netto="445.00",
         weight_kg="16.00", battery_type=BatteryType.LIFEPO4, output_power_w=1800),
    dict(sku="EMX-BLUETTI-AC200PL", name="AC200PL", price_eur_netto="764.00",
         weight_kg="27.90", battery_type=BatteryType.LIFEPO4, output_power_w=2400,
         features="Розширювана додатковими акумуляторами (модульна серія)"),
    dict(sku="EMX-BLUETTI-PREMIUM30V2", name="Premium 30 V2", price_eur_netto="149.00",
         weight_kg="4.30", dimensions="250×178×168", battery_type=BatteryType.LIFEPO4, output_power_w=600),
    dict(sku="EMX-BLUETTI-PREMIUM100V2", name="Premium 100 V2", price_eur_netto="365.00",
         battery_type=BatteryType.LIFEPO4, output_power_w=1800),
    dict(sku="EMX-BLUETTI-PREMIUM200V2", name="Premium 200 V2", price_eur_netto="740.00",
         weight_kg="24.20", dimensions="350×250×324", battery_type=BatteryType.LIFEPO4, output_power_w=2700),
    dict(sku="EMX-BLUETTI-APEX300", name="Apex300", price_eur_netto="1184.00",
         weight_kg="44.00", dimensions="690×490×500", battery_type=BatteryType.LIFEPO4, output_power_w=3840,
         capacity_wh=2765, features="Розширюється до 58 кВт·год додатковими батарейними модулями"),
]

# --- 3 Anker (draft: балконні станції, інша товарна категорія — без ціни й фото, ТЗ-виняток) ---
ANKER = [
    dict(
        sku="EMX-ANKER-SOLARBANK2-E1600PRO", name="SOLIX Solarbank 2 E1600 Pro",
        weight_kg="21.80", battery_type=BatteryType.LIFEPO4, output_power_w=800, capacity_wh=1600,
        short_description="Балконна станція (не портативна) — накопичувач із вбудованим мікроінвертором",
        features="Plug & Play: панелі → накопичувач → розетка; вбудований мікроінвертор",
    ),
    dict(
        sku="EMX-ANKER-E1600-AC", name="SOLIX Solarbank 2 E1600 AC",
        weight_kg="21.80", battery_type=BatteryType.LIFEPO4, output_power_w=800, capacity_wh=1600,
        short_description="Балконна станція (не портативна) — версія AC для підключення через розетку",
        features="Підключення до існуючого мікроінвертора через звичайну розетку; 1200 Вт off-grid режим",
    ),
    dict(
        sku="EMX-ANKER-SOLARBANK3-E2700PRO", name="SOLIX Solarbank 3 E2700 Pro",
        weight_kg="29.20", battery_type=BatteryType.LIFEPO4, output_power_w=1800, capacity_wh=2680,
        short_description="Балконна станція (не портативна) — флагманський накопичувач «все в одному»",
        features="Мікроінвертор + інтелектуальна система керування; до 4 MPP-трекерів; IP65",
    ),
]


class Command(BaseCommand):
    help = "Seed каталогу Euromaxi UA: 21 SKU (10 Jackery + 8 Bluetti + 3 Anker-draft)."

    @transaction.atomic
    def handle(self, *args, **options):
        jackery = Brand.objects.get_or_create(name="Jackery")[0]
        bluetti = Brand.objects.get_or_create(name="Bluetti")[0]
        anker = Brand.objects.get_or_create(name="Anker")[0]

        created, updated = 0, 0
        for brand, rows in ((jackery, JACKERY_MASTER + JACKERY_DRAFT), (bluetti, BLUETTI), (anker, ANKER)):
            for row in rows:
                sku = row.pop("sku")
                name = row.pop("name")
                price_eur = row.pop("price_eur_netto", None)
                defaults = {
                    "brand": brand,
                    "name": name,
                    "price_eur_netto": Decimal(price_eur) if price_eur else None,
                    "weight_kg": Decimal(row.pop("weight_kg")) if row.get("weight_kg") else None,
                    "dimensions": row.pop("dimensions", ""),
                    "battery_type": row.pop("battery_type", ""),
                    "output_power_w": row.pop("output_power_w", None),
                    "capacity_wh": row.pop("capacity_wh", None),
                    "outputs": row.pop("outputs", ""),
                    "charging": row.pop("charging", ""),
                    "features": row.pop("features", ""),
                    "short_description": row.pop("short_description", ""),
                    "is_specs_confirmed": row.pop("is_specs_confirmed", False),
                    # ціна/публікація — навмисно НЕ активуємо, доки клієнт не підтвердить курс/націнку
                    "price_uah": None,
                    "is_price_confirmed": False,
                    "is_active": False,
                }
                obj, was_created = Product.objects.update_or_create(sku=sku, defaults=defaults)
                created += int(was_created)
                updated += int(not was_created)

        self.stdout.write(self.style.SUCCESS(
            f"Каталог заповнено: {created} нових, {updated} оновлено. "
            f"Усі товари is_active=False — активуйте вручну після recalc_prices."
        ))
