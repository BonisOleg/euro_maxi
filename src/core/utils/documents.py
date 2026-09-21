"""SEC-05: валідація PDF для інструкцій і сертифікатів товару."""
from __future__ import annotations

import os

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

MAX_PDF_BYTES = 15 * 1024 * 1024
PDF_MAGIC = b"%PDF"


def validate_pdf(value) -> None:
    """Лише PDF: розширення + magic bytes + розмір. Без SVG/скриптів."""
    if value is None:
        return
    name = getattr(value, "name", "") or ""
    ext = os.path.splitext(name)[1].lower()
    if ext != ".pdf":
        raise ValidationError("Дозволені лише файли PDF.")
    size = getattr(value, "size", None)
    if size is not None and size > MAX_PDF_BYTES:
        raise ValidationError(
            f"Файл завеликий (макс. {filesizeformat(MAX_PDF_BYTES)})."
        )
    pos = value.tell() if hasattr(value, "tell") else None
    try:
        header = value.read(len(PDF_MAGIC))
    except Exception as exc:
        raise ValidationError("Не вдалося прочитати файл.") from exc
    finally:
        if pos is not None and hasattr(value, "seek"):
            value.seek(pos)
    if header != PDF_MAGIC:
        raise ValidationError("Файл не є коректним PDF.")
