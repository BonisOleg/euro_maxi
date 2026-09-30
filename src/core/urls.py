from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/suggest/", views.SearchSuggestView.as_view(), name="search_suggest"),
    path("search/", views.SearchView.as_view(), name="search"),
]
