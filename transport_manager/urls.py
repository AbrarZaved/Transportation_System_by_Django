from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path("subscription/", views.subscription, name="subscription"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("today_schedules/", views.today_schedules, name="today_schedules"),
    path("edit_schedule/", views.edit_schedule, name="edit_schedule"),
    path("delete_schedule/", views.delete_schedule, name="delete_schedule"),
    path("filter_route/", views.filter_route, name="filter_route"),
    path("assign_schedule/", views.assign_schedule, name="assign_schedule"),
    path(
        "manage_drivers_buses/", views.manage_drivers_buses, name="manage_drivers_buses"
    ),
    path("route_management/", views.route_management, name="route_management"),
    path("route_stoppages", views.route_stoppages, name="route_stoppages"),
    path("add_route", views.add_route, name="add_route"),
    path("update_route/<int:id>", views.update_route, name="update_route"),
    path("add_notice/", views.add_notice, name="add_notice"),
    path("view_notices/", views.view_notices, name="view_notices"),
    path("send_location/", csrf_exempt(views.send_location), name="send_location"),
    # Legacy API endpoints (maintained for backward compatibility)
    path(
        "trips/<int:driver_id>/<str:auth_token>/",
        csrf_exempt(views.trips),
        name="trips",
    ),
    path("trip_complete/", csrf_exempt(views.trip_complete), name="trip_complete"),
    path("api/trips/today/", views.trips_today, name="api_trips_today"),
]
