#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

from decouple import config


def main() -> None:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        config("DJANGO_SETTINGS_MODULE", default="config.settings.develop"),
    )
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не вдалося імпортувати Django. Активуйте venv: source venv/bin/activate"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
