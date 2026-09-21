from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Ядро сайту"

    def ready(self) -> None:
        from core.signals_images import connect_webp_signals

        connect_webp_signals()
