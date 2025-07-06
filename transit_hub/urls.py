from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("search_route/", views.search_route, name="search_route"),
    path("about_us", views.about_us, name="about_us"),
    path("contact_us", views.contact_us, name="contact_us"),
    path("api/route_stoppage/", views.RouteStoppage.as_view(), name="route_stoppage"),
    path(
        "api/route_stoppage/<int:id>",
        views.RouteStoppage.as_view(),
        name="route_stoppage",
    ),
    path("api/route_details/", views.RouteDetails.as_view(), name="route_stoppage"),
    path(
        "api/route_details/<int:id>",
        views.RouteDetails.as_view(),
        name="route_stoppage",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
