from django.urls import path
from django.views import csrf
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path("my_account", views.my_account, name="my_account"),
    path("login_request", views.login_request, name="login_request"),
    path("diu_admin/", views.admin_login, name="diu_admin"),
    path("driver_login/", csrf_exempt(views.driver_login), name="driver_login"),
    path("logout/", views.admin_logout, name="logout"),
    path("register", views.register_request, name="register"),
    path("verify_otp", views.verify_otp_view, name="verify_otp"),
    path("resend_otp", views.resend_otp, name="resend_otp"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("sign_out", views.sign_out, name="sign_out"),
    path("get_history", csrf_exempt(views.get_history), name="get_history"),
    path("delete_history/<int:id>/", views.delete_history, name="delete_history"),
    path("error/", views.social_auth_error, name="social_auth_error"),
]
