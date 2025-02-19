from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("api/route_stoppage/", views.RouteStoppage.as_view(), name="route_stoppage"),
    path(
        "api/route_stoppage/<int:id>",
        views.RouteStoppage.as_view(),
        name="route_stoppage",
    ),
    path("api/route_details/", views.RouteDetails.as_view(), name="route_stoppage"),
    path("api/route_details/<int:id>", views.RouteDetails.as_view(), name="route_stoppage"),
]
