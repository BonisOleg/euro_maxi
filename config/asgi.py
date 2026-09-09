"""ASGI-конфіг для Euromaxi UA (не використовується у v1, для сумісності)."""
import os
import sys
from pathlib import Path

from decouple import config
from django.core.asgi import get_asgi_application

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    config("DJANGO_SETTINGS_MODULE", default="config.settings.production"),
)

application = get_asgi_application()
