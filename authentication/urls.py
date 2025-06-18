from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path("authentication", views.auth, name="student_auth"),
    path("my_account", views.my_account, name="my_account"),
    path("student_auth", csrf_exempt(views.student_auth), name="student_auth"),
    path("sign_out", views.sign_out, name="sign_out"),
    path("get_history", csrf_exempt(views.get_history), name="get_history"),
    path("delete_history/<int:id>/", views.delete_history, name="delete_history"),
]
