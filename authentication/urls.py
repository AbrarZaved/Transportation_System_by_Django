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
    path("reviews/", views.reviews_page, name="reviews"),
    path("submit_review/", csrf_exempt(views.submit_review), name="submit_review"),
    path("delete_review/<int:review_id>/", views.delete_review, name="delete_review"),
    path(
        "api/reviews_carousel/", views.get_reviews_for_carousel, name="reviews_carousel"
    ),
    path("contact_us", views.contact_us, name="contact_us"),
    # Support Tickets - Student
    path("support/", views.support_tickets, name="support_tickets"),
    path("support/create/", views.create_ticket, name="create_ticket"),
    path("support/<str:ticket_id>/", views.ticket_detail, name="ticket_detail"),
    # Support Tickets - Admin
    path("admin/support/", views.admin_support_tickets, name="admin_support_tickets"),
    path(
        "admin/support/<str:ticket_id>/",
        views.admin_ticket_detail,
        name="admin_ticket_detail",
    ),
]
