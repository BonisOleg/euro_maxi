import logging

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from . import monobank
from .forms import CheckoutForm
from .services import CartValidationError, create_order_from_cart

logger = logging.getLogger(__name__)


class CartView(TemplateView):
    """Кошик рендериться на клієнті з localStorage (js/cart.js) — сторінка лише каркас."""

    template_name = "commerce/cart.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Кошик"
        return ctx


class CheckoutView(View):
    template_name = "commerce/checkout.html"

    def get(self, request):
        form = CheckoutForm()
        return render(request, self.template_name, {"form": form, "page_title": "Оформлення замовлення"})

    def post(self, request):
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(
                request, self.template_name, {"form": form, "page_title": "Оформлення замовлення"}
            )

        try:
            order = create_order_from_cart(
                form_data=form.cleaned_data, cart_items=form.cleaned_data["cart_data"]
            )
        except CartValidationError as exc:
            messages.error(request, str(exc))
            return render(
                request, self.template_name, {"form": form, "page_title": "Оформлення замовлення"}
            )

        invoice = monobank.create_invoice(
            order_number=order.order_number,
            amount_uah=order.total_uah,
            redirect_url=request.build_absolute_uri(reverse("commerce:thanks", args=[order.order_number])),
            webhook_url=request.build_absolute_uri(reverse("commerce:monobank_webhook")),
        )
        order.monobank_invoice_id = invoice.invoice_id
        order.save(update_fields=["monobank_invoice_id"])

        # SEC-01/LS-15: гостьовий доступ до деталей замовлення скоупимо через сесію,
        # а не голий order_number у URL — сторонній, хто підгледів лінк, не побачить ПІБ/суму.
        allowed = request.session.get("euromaxi_order_numbers", [])
        allowed = [*allowed, order.order_number][-20:]
        request.session["euromaxi_order_numbers"] = allowed

        if invoice.is_sandbox:
            logger.info("Sandbox-оплата: пропускаємо редірект на Monobank для %s", order.order_number)
            return redirect("commerce:thanks", order_number=order.order_number)

        return redirect(invoice.pay_url)


class ThanksView(TemplateView):
    """SEC-01/LS-15: деталі замовлення (ПІБ у майбутньому, сума) показуємо лише
    якщо order_number є у сесії поточного відвідувача (виставляється при створенні
    замовлення в CheckoutView) — голий order_number з URL сам по собі не авторизує."""

    template_name = "commerce/thanks.html"

    def get_context_data(self, **kwargs):
        from .models import Order

        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Дякуємо за замовлення"

        order_number = kwargs.get("order_number")
        allowed = self.request.session.get("euromaxi_order_numbers", [])
        ctx["order"] = (
            Order.objects.filter(order_number=order_number).first()
            if order_number in allowed
            else None
        )
        return ctx


@method_decorator(csrf_exempt, name="dispatch")
class MonobankWebhookView(View):
    """Webhook Monobank — оновлює статус оплати.

    LS-36/SEC-07: `csrf_exempt` тут обґрунтований — Monobank як зовнішній сервер
    фізично не може надіслати наш CSRF-токен, авторизація вебхука має йти через
    перевірку підпису (X-Sign, ECDSA), а не через сесійний CSRF. Підпис поки не
    перевіряється, доки немає реального токена/публічного ключа еквайрингу
    (ТЗ п.4.4, відкрите питання) — тож і бізнес-логіка обробки статусу свідомо
    не реалізована (501), щоб не приймати неавтентифіковані команди."""

    def post(self, request):
        logger.warning("Отримано Monobank webhook, але інтеграція ще не активна (немає токена).")
        return HttpResponse(
            "Monobank webhook integration is not enabled yet.", status=501, content_type="text/plain"
        )
