from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path(
        "<slug:slug>/docs/<int:pk>/download/",
        views.product_document_download,
        name="document_download",
    ),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
