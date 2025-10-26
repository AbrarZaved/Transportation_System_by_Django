from django.urls import path
from django.views import csrf
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path("my_account", views.my_account, name="my_account"),
    path("login_request", views.login_request, name="login_request"),
    path("register", views.register_request, name="register"),
    path("verify_otp", csrf_exempt(views.verify_otp_view), name="verify_otp"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("sign_out", views.sign_out, name="sign_out"),
    path("get_history", csrf_exempt(views.get_history), name="get_history"),
    path("delete_history/<int:id>/", views.delete_history, name="delete_history"),
    path("error/", views.social_auth_error, name="social_auth_error"),
]
