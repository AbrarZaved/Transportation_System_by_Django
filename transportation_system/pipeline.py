from django.contrib import messages
from django.shortcuts import redirect
from authentication.models import Student
from authentication.views import send_otp_view


def create_or_update_student(backend, user, details, *args, **kwargs):
    """
    Handle DIU email validation, student creation/updating,
    and session setup in a single step.
    """
    email = details.get("email")
    full_name = details.get("fullname")
    request = kwargs.get("request")

    # Validate email domain
    if not email or email.split("@")[-1].lower() != "diu.edu.bd":
        if request:
            return redirect("social_auth_error")  # Non-DIU email
        return None  # In case no request object is present

    # Create or update Student entry
    student, created = Student.objects.get_or_create(
        email=email, defaults={"name": full_name}
    )
    if created:
        otp_sent = send_otp_view(student)
        if otp_sent:
            messages.warning(request, "OTP Sent!")
            return redirect("verify_otp")
        else:
            return redirect("social_auth_error")

    # Setup session
    if request and student.verified:
        request.session["username"] = student.username
        request.session["is_student_authenticated"] = True
        request.session.set_expiry(3600)
    else:
        if request:
            return redirect("social_auth_error")  # Unverified email