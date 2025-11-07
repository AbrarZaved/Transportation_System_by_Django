from functools import wraps
import json
from django.contrib import messages
from django.core.validators import validate_email
from django.db import models
from django.forms import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from social_core.backends import username
from authentication.email import create_email_otp, send_otp_email
from authentication.models import EmailOTP, Preference, Student
from threading import Thread


def student_wrapper(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        username = request.session.get("username")
        student = get_object_or_404(Student, username=username)
        if student.verified or not username:
            return redirect("index")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


@student_wrapper
def verify_otp_view(request):
    if request.method == "POST":
        otp_input = json.loads(request.body).get("otp")
        otp_obj = EmailOTP.objects.filter(otp=otp_input).last()

        if otp_obj and not otp_obj.is_expired():
            otp_obj.user.verified = True
            otp_obj.user.save()
            request.session["username"] = otp_obj.user.username
            request.session["is_student_authenticated"] = True
            messages.success(request, "Email verified successfully!")
            return JsonResponse({"success": True})
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, "authentication/verify_otp.html")


@csrf_exempt
def resend_otp(request):
    if request.method == "POST":
        try:
            username = request.session.get("username")
            if not username:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Session expired. Please register again.",
                    },
                    status=400,
                )

            try:
                student = Student.objects.get(username=username)
                if student.verified:
                    return JsonResponse(
                        {"success": False, "message": "Account already verified."},
                        status=400,
                    )
            except Student.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "Student not found."}, status=400
                )

            # Delete any existing OTPs for this user
            EmailOTP.objects.filter(user=student).delete()

            # Create and send new OTP
            otp = create_email_otp(student)
            email_thread = Thread(target=send_otp_email, args=(student, otp))
            email_thread.daemon = True
            email_thread.start()

            return JsonResponse(
                {
                    "success": True,
                    "message": "New OTP has been sent to your email address.",
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Failed to resend OTP. Please try again.",
                },
                status=500,
            )

    return JsonResponse(
        {"success": False, "message": "Invalid request method."}, status=405
    )


def my_account(request):
    username = request.session.get("username")
    if not username:
        return redirect("index")

    student = get_object_or_404(Student, username=username)
    total_searches = (
        Preference.objects.filter(student=student)
        .aggregate(total_searches=models.Sum("total_searches"))
        .get("total_searches", 0)
    )
    return render(
        request,
        "authentication/my_account.html",
        {"student": student, "total_searches": total_searches if total_searches else 0},
    )


def login_request(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        password = request.POST.get("password", "").strip()

        if not student_id or not password:
            messages.error(request, "Please provide both Student ID and password.")
            return redirect("index")

        student = Student.objects.filter(student_id=student_id, verified=True).first()

        if not student:
            messages.error(request, "Student ID not found or account not verified.")
            return redirect("index")

        if not student.check_password(password):
            messages.error(request, "Incorrect password. Please try again.")
            return redirect("index")

        # Login successful
        request.session["username"] = student.username
        request.session["is_student_authenticated"] = True
        request.session.set_expiry(3600)  # 1 hour
        messages.success(request, "Logged In!", extra_tags=student.name)
        return redirect("index")

    return redirect("index")


def register_request(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        password = request.POST.get("password", "").strip()
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()

        # Validate required fields
        if not all([student_id, password, name, email, phone_number]):
            messages.error(request, "All fields are required.")
            return redirect("index")

        # Check if student ID already exists
        if Student.objects.filter(student_id=student_id).exists():
            messages.error(
                request, "Student ID already exists. Please use a different ID."
            )
            return redirect("index")

        # Check if email already exists
        if Student.objects.filter(email=email).exists():
            messages.error(
                request, "Email already registered. Please use a different email."
            )
            return redirect("index")

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect("index")

        # Validate password length
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect("index")

        try:
            student = Student(
                student_id=student_id,
                name=name,
                email=email,
                phone_number=phone_number,
            )
            student.set_password(password)
            student.save()
            request.session["username"] = student.username

            # Send OTP asynchronously using threading
            otp = create_email_otp(student)
            email_thread = Thread(target=send_otp_email, args=(student, otp))
            email_thread.daemon = True  # Thread will die when main program exits
            email_thread.start()

            messages.success(
                request,
                "Registration successful! Please check your email for OTP verification.",
            )
            return redirect("verify_otp")
        except Exception as e:
            messages.error(request, "Registration failed. Please try again.")
            return redirect("index")

    return redirect("index")


def sign_out(request):
    request.session.flush()
    messages.success(request, "Logged Out!")
    return redirect("index")


def get_history(request):
    try:
        if request.method == "POST":
            student_id = json.loads(request.body).get("studentId").strip()
            student = Student.objects.filter(student_id=student_id).first()
            if not student:
                return JsonResponse({"history": []})

            history_qs = Preference.objects.filter(student=student).order_by(
                "-created_at"
            )
            history = [
                {"id": item.id, "place": item.searched_locations} for item in history_qs
            ]
            return JsonResponse({"history": history})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)


@csrf_exempt
def delete_history(request, id):
    if request.method == "DELETE":
        Preference.objects.filter(id=id).delete()
        return JsonResponse({"status": "deleted"})
    return JsonResponse({"error": "Invalid method"}, status=405)


def edit_profile(request):
    if request.method == "POST":
        username = request.session.get("username")
        student = get_object_or_404(Student, username=username)

        # Fields to check in POST
        fields = ["name", "phone_number", "dept_name", "batch_code", "student_id"]

        for field in fields:
            value = request.POST.get(field, "").strip()
            if value and value != getattr(student, field):
                setattr(student, field, value)

        # Handle profile picture separately
        profile_pic = request.FILES.get("profile_pic")
        if profile_pic:
            student.profile_pic = profile_pic

        student.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect("my_account")


def social_auth_error(request):
    messages.error(request, "Not Allowed")
    return redirect("index")
