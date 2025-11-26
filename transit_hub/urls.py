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
    path("view_bus", views.view_bus, name="view_bus"),
    path("api/stoppages/", views.get_all_stoppages, name="get_all_stoppages"),
    path("api/active_buses/", views.get_active_buses_api, name="get_active_buses_api"),
    path("api/route_stoppage/", views.RouteStoppage.as_view(), name="route_stoppage"),
    path(
        "api/route_stoppage/<int:id>",
        views.RouteStoppage.as_view(),
        name="route_stoppage",
    ),
    path("api/route_details/", views.RouteDetails.as_view(), name="route_details"),
    path(
        "api/route_details/<int:id>",
        views.RouteDetails.as_view(),
        name="route_details_id",
    ),
    path(
        "api/bus_location/<str:bus_name>/",
        csrf_exempt(views.get_bus_location),
        name="get_bus_location",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
