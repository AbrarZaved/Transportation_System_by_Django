from threading import Thread
from django.contrib import messages
from django.shortcuts import redirect
from authentication.email import create_email_otp, send_otp_email
from authentication.models import Student



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
        request.session["username"] = student.username
        otp = create_email_otp(student)
        email_thread = Thread(target=send_otp_email, args=(student, otp))
        email_thread.daemon = True  # Thread will die when main program exits
        email_thread.start()
        return redirect("verify_otp")  # New student, redirect to OTP verification


    # Setup session
    if request and student.verified:
        request.session["username"] = student.username
        messages.success(request, "Logged In!", extra_tags=student.name)
        request.session["is_student_authenticated"] = True
        request.session.set_expiry(3600)
    else:
        if request:
            return redirect("social_auth_error")  # Unverified email