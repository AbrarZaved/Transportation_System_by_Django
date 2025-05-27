from django.urls import path
from . import views


urlpatterns = [
    path("my_account", views.my_account, name="my_account"),
    path("sign_in", views.sign_in, name="sign_in"),
    path("sign_out", views.sign_out, name="sign_out"),
]
