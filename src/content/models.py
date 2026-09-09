from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class Page(models.Model):
    """Статична сторінка (Про нас, Доставка й оплата, Публічна оферта, Політика)."""

    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("Слаг", max_length=100, unique=True)
    body = models.TextField("Вміст (HTML)", blank=True)
    meta_description = models.CharField("Meta description", max_length=300, blank=True)
    is_published = models.BooleanField("Опубліковано", default=True)
    updated_at = models.DateTimeField("Оновлено", auto_now=True)

    class Meta:
        verbose_name = "Сторінка"
        verbose_name_plural = "Сторінки"
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("content:page_detail", kwargs={"slug": self.slug})


class ContactMessage(models.Model):
    """Звернення з форми контактів."""

    name = models.CharField("Ім'я", max_length=100)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    email = models.EmailField("Email", blank=True)
    message = models.TextField("Повідомлення")
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Отримано", auto_now_add=True)

    class Meta:
        verbose_name = "Звернення"
        verbose_name_plural = "Звернення"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.created_at:%d.%m.%Y %H:%M}"


class SiteSettings(models.Model):
    """Singleton: контакти, реквізити, керовані через адмінку (ТЗ п.4.6)."""

    phone = models.CharField("Телефон", max_length=32, default="+38 (067) 555-12-34")
    email = models.EmailField("Email", default="info@euromaxi.ua")
    address = models.CharField("Адреса/офіс", max_length=255, blank=True)
    working_hours = models.CharField("Графік роботи", max_length=200, blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    facebook_url = models.URLField("Facebook", blank=True)
    telegram_url = models.URLField("Telegram", blank=True)
    monobank_jar_url = models.URLField("Monobank (посилання на банку)", blank=True)

    class Meta:
        verbose_name = "Налаштування сайту"
        verbose_name_plural = "Налаштування сайту"

    def __str__(self) -> str:
        return "Налаштування сайту"

    def clean(self):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("Налаштування сайту можуть існувати лише в одному екземплярі.")

    @classmethod
    def get_solo(cls) -> "SiteSettings":
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj
