from django.urls import path
from . import views


urlpatterns = [
    path("subscription/", views.subscription, name="subscription"),
    path("diu_admin/", views.admin_login, name="diu_admin"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("today_schedules/", views.today_schedules, name="today_schedules"),
    path("filter_route/", views.filter_route, name="filter_route"),
    path("assign_schedule/", views.assign_schedule, name="assign_schedule"),
    path(
        "manage_drivers_buses/", views.manage_drivers_buses, name="manage_drivers_buses"
    ),
    path("logout/", views.admin_logout, name="logout"),
    path("route_management/", views.route_management, name="route_management"),
    path("route_stoppages", views.route_stoppages, name="route_stoppages"),
    path("add_route", views.add_route, name="add_route"),
    path("update_route/<int:id>", views.update_route, name="update_route"),
]
