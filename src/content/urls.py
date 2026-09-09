from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("contacts/", views.ContactsView.as_view(), name="contacts"),
    path("p/<slug:slug>/", views.PageDetailView.as_view(), name="page_detail"),
]
