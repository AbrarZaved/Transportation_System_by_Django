from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path("", views.index, name="index"),
    path("search_route", csrf_exempt(views.search_route), name="search_route"),
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
