from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # LS-40: honeypot — приховане поле, невидиме людині (CSS в шаблоні).
    # Боти зазвичай заповнюють усі поля форми; порожнє значення — ознака людини.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("phone") and not cleaned.get("email"):
            raise forms.ValidationError("Вкажіть телефон або email для зв'язку.")
        return cleaned

    def clean_website(self):
        # Honeypot заповнений — тихо відхиляємо як «звичайну» помилку валідації,
        # без підказки боту, що саме спрацювало.
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Помилка форми.")
        return value
