"""Monobank Acquiring API — тонка обгортка. Без токена працює у sandbox-режимі (заглушка).

Реальна інтеграція: POST https://api.monobank.ua/api/merchant/invoice/create
Документація: https://api.monobank.ua/docs/acquiring.html
Підпис вебхука перевіряється окремо у webhook-view (X-Sign, ECDSA) — не реалізовано,
доки клієнт не надасть токен еквайрингу (ТЗ п.4.4, відкрите питання).
"""
import logging
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger(__name__)

MONOBANK_INVOICE_URL = "https://api.monobank.ua/api/merchant/invoice/create"


@dataclass
class InvoiceResult:
    invoice_id: str
    pay_url: str
    is_sandbox: bool


def create_invoice(*, order_number: str, amount_uah, redirect_url: str, webhook_url: str) -> InvoiceResult:
    """Створює інвойс на оплату. Без MONOBANK_TOKEN — повертає sandbox-заглушку (без реального платежу)."""
    if not settings.MONOBANK_TOKEN:
        logger.info(
            "MONOBANK_TOKEN не задано — sandbox-режим для замовлення %s", order_number
        )
        return InvoiceResult(
            invoice_id=f"sandbox-{order_number}",
            pay_url="",
            is_sandbox=True,
        )

    # TODO: реальний виклик Monobank API після отримання токена від клієнта.
    # amount у копійках (int), signature/webhook — за документацією еквайрингу.
    raise NotImplementedError(
        "Реальна інтеграція Monobank не реалізована — очікуємо токен від клієнта."
    )
