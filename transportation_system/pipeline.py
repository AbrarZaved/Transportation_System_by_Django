from django.shortcuts import redirect
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
    if not created and full_name and student.name != full_name:
        student.name = full_name
        student.save()

    # Setup session
    if request:
        request.session["username"] = student.username
        request.session["is_student_authenticated"] = True
        request.session.set_expiry(3600)
