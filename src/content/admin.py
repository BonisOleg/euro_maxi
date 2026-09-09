from django.contrib import admin
from django.db import models as db_models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import ContactMessage, Page, SiteSettings


@admin.register(Page)
class PageAdmin(ModelAdmin):
    list_display = ["title", "slug", "is_published", "updated_at"]
    search_fields = ["title", "slug"]
    prepopulated_fields = {"slug": ["title"]}
    # Редактор Trix (вбудований у django-unfold) замість голого textarea з HTML —
    # клієнт редагує текст сторінки візуально, без знання HTML.
    formfield_overrides = {db_models.TextField: {"widget": WysiwygWidget}}


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ["name", "phone", "email", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    list_display = ["__str__", "phone", "email"]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
