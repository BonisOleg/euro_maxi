"""WSGI-конфіг для Euromaxi UA."""
import os
import sys
from pathlib import Path

from decouple import config
from django.core.wsgi import get_wsgi_application

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    config("DJANGO_SETTINGS_MODULE", default="config.settings.production"),
)

application = get_wsgi_application()
