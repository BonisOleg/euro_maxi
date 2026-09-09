import json

from django import forms

from .models import NovaPoshtaType


class CheckoutForm(forms.Form):
    """Дані покупця + доставка. Кошик приходить окремо у cart_data (JSON з JS localStorage)."""

    full_name = forms.CharField(label="ПІБ", max_length=150)
    phone = forms.CharField(label="Телефон", max_length=32)
    email = forms.EmailField(label="Email", required=False)
    comment = forms.CharField(label="Коментар", required=False, widget=forms.Textarea)

    city = forms.CharField(label="Місто", max_length=120)
    np_type = forms.ChoiceField(
        label="Спосіб отримання", choices=NovaPoshtaType.choices, initial=NovaPoshtaType.WAREHOUSE
    )
    np_point = forms.CharField(label="Відділення / адреса", max_length=255)

    agree = forms.BooleanField(label="Згода з офертою", required=True)

    # Прихований JSON: [{"sku": "...", "qty": N}, ...] — заповнюється JS з localStorage-кошика
    cart_data = forms.CharField(widget=forms.HiddenInput)

    def clean_cart_data(self):
        raw = self.cleaned_data["cart_data"]
        try:
            items = json.loads(raw)
        except (TypeError, ValueError) as exc:
            raise forms.ValidationError("Кошик пошкоджено, спробуйте ще раз.") from exc

        if not isinstance(items, list) or not items:
            raise forms.ValidationError("Кошик порожній.")

        merged = {}
        for entry in items:
            sku = str(entry.get("sku", "")).strip()
            try:
                qty = int(entry.get("qty", 0))
            except (TypeError, ValueError):
                qty = 0
            if not sku or qty <= 0:
                continue
            merged[sku] = min(merged.get(sku, 0) + qty, 20)

        if not merged:
            raise forms.ValidationError("Кошик порожній.")
        return [{"sku": sku, "qty": qty} for sku, qty in merged.items()]
