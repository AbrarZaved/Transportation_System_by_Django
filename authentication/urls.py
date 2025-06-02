from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path("my_account", views.my_account, name="my_account"),
    path("sign_in", csrf_exempt(views.sign_in), name="sign_in"),
    path("sign_out", views.sign_out, name="sign_out"),
    path("get_history", csrf_exempt(views.get_history), name="get_history"),
    path("delete_history/<int:id>/", views.delete_history, name="delete_history"),
]
