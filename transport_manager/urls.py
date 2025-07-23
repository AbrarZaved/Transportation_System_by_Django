from django.urls import path
from . import views


urlpatterns = [
    path("subscription/", views.subscription, name="subscription"),
    path("diu_admin/", views.admin_login, name="diu_admin"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.admin_logout, name="logout"),
]
