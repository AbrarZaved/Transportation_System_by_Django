from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from transit_hub import views

urlpatterns = [
    path(
        "",
        include("authentication.urls"),
    ),
    path("", include("transit_hub.urls")),
    path("", include("transport_manager.urls")),
    path("auth/", include("social_django.urls", namespace="social")),
    path("admin/", admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
