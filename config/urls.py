from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

admin.site.site_url = "/"

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("healthz/", lambda request: HttpResponse("ok")),
    path("catalog/", include("catalog.urls")),
    path("", include("commerce.urls")),
    path("", include("content.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
