from django.urls import path

from . import views

app_name = "commerce"

urlpatterns = [
    path("cart/", views.CartView.as_view(), name="cart"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("thanks/<str:order_number>/", views.ThanksView.as_view(), name="thanks"),
    path("webhooks/monobank/", views.MonobankWebhookView.as_view(), name="monobank_webhook"),
]
