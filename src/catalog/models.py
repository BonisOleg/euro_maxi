from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Brand(models.Model):
    """Виробник зарядних станцій (Jackery, Bluetti, Anker)."""

    name = models.CharField("Назва", max_length=100, unique=True)
    slug = models.SlugField("Слаг", max_length=100, unique=True, blank=True)
    logo = models.ImageField("Логотип", upload_to="brands/", blank=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренди"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BatteryType(models.TextChoices):
    LIFEPO4 = "lifepo4", "LiFePO4"
    LI_ION = "li_ion", "Li-ion (NMC)"


class Product(models.Model):
    """Портативна/домашня зарядна станція — єдина товарна категорія (ТЗ п.5.2)."""

    brand = models.ForeignKey(
        Brand, verbose_name="Бренд", on_delete=models.PROTECT, related_name="products"
    )
    sku = models.CharField("SKU", max_length=32, unique=True)
    name = models.CharField("Назва", max_length=200)
    slug = models.SlugField("Слаг", max_length=220, unique=True, blank=True)

    # --- Ключові характеристики (Правки_до_ТЗ.md — пріоритетні поля) ---
    capacity_wh = models.PositiveIntegerField("Ємність, Вт·год", null=True, blank=True)
    output_power_w = models.PositiveIntegerField(
        "Вихідна потужність, Вт", null=True, blank=True
    )
    battery_type = models.CharField(
        "Тип акумулятора", max_length=16, choices=BatteryType.choices, blank=True
    )
    outputs = models.TextField(
        "Роз'єми виходу", blank=True, help_text="Наприклад: 3×AC, 2×USB-C PD100W, 2×USB-A, DC"
    )
    charging = models.TextField(
        "Варіанти заряджання", blank=True, help_text="Наприклад: AC 0-80% за 1 год, сонячна панель до 200Вт"
    )
    features = models.TextField(
        "Особливості", blank=True, help_text="UPS, застосунок, LED-фонарик тощо — через кому"
    )
    weight_kg = models.DecimalField(
        "Вага, кг", max_digits=5, decimal_places=2, null=True, blank=True
    )
    dimensions = models.CharField(
        "Габарити (ДxШxВ, мм)", max_length=50, blank=True
    )

    short_description = models.CharField("Короткий опис", max_length=300, blank=True)
    description = models.TextField("Опис", blank=True)

    # --- Ціни (ТЗ — тільки UAH на сайті; EUR netto — службове поле для розрахунку) ---
    price_eur_netto = models.DecimalField(
        "Закупівельна ціна netto, EUR", max_digits=10, decimal_places=2, null=True, blank=True
    )
    price_uah = models.DecimalField(
        "Роздрібна ціна, UAH",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Порожньо, доки не підтверджено курс і націнку — товар неактивний.",
    )
    old_price_uah = models.DecimalField(
        "Стара ціна (для акції), UAH", max_digits=10, decimal_places=2, null=True, blank=True
    )

    is_active = models.BooleanField(
        "Активний (видимий на сайті)",
        default=False,
        help_text="Автоматично False, доки немає ціни UAH — вмикається вручну після перевірки.",
    )
    is_hit = models.BooleanField("Хіт продажів", default=False)
    is_new = models.BooleanField("Новинка", default=False)

    is_price_confirmed = models.BooleanField(
        "Ціна підтверджена", default=False, help_text="SEC-02: без цього товар не можна продавати."
    )
    is_specs_confirmed = models.BooleanField(
        "Характеристики звірені з сайту виробника", default=False
    )

    created_at = models.DateTimeField("Створено", auto_now_add=True)
    updated_at = models.DateTimeField("Оновлено", auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ["-is_hit", "brand__name", "name"]

    def __str__(self) -> str:
        return f"{self.brand} {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.name}")
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    @property
    def is_sellable(self) -> bool:
        """SEC-02: продаж лише за активної, підтвердженої, ненульової ціни."""
        return bool(self.is_active and self.is_price_confirmed and self.price_uah)

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()


class ProductImage(models.Model):
    """Фото товару. placeholder=True — заглушка, доки немає реального фото."""

    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField("Зображення", upload_to="products/")
    alt = models.CharField("Alt-текст", max_length=200, blank=True)
    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_primary = models.BooleanField("Головне фото", default=False)
    is_placeholder = models.BooleanField("Заглушка (немає реального фото)", default=False)

    class Meta:
        verbose_name = "Фото товару"
        verbose_name_plural = "Фото товарів"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.product} — фото #{self.order}"
