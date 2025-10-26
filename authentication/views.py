import json
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.db import models
from django.forms import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from social_core.backends import username
from authentication.email import create_email_otp, send_otp_email
from authentication.models import EmailOTP, Preference, Student


def student_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("is_student_authenticated"):
            messages.error(request, "Please log in to access this page.")
            return redirect("index")
        return view_func(request, *args, **kwargs)

    return wrapper


def send_otp_view(request):
    otp = create_email_otp(request.user)
    send_otp_email(request.user, otp)
    messages.success(request, "OTP sent to your email!")
    return redirect("verify_otp")


def verify_otp_view(request):
    if request.method == "POST":
        otp_input = request.POST.get("otp")
        otp_obj = EmailOTP.objects.filter(user=request.user, otp=otp_input).last()

        if otp_obj and not otp_obj.is_expired():
            request.user.verified = True
            request.user.save()
            messages.success(request, "Email verified successfully!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, "verify_otp.html")


@student_login_required
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


def student_auth(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Invalid JSON format."}, status=400
        )

    mode = data.get("mode", "").strip()
    student_id = data.get("student_id", "").strip()
    password = data.get("password", "").strip()

    if not student_id or not password:
        return JsonResponse(
            {"success": False, "message": "Student ID and password are required."},
            status=400,
        )

    if mode == "signin":
        student = Student.objects.filter(student_id=student_id).first()
        if not student:
            return JsonResponse(
                {"success": False, "message": "Student ID does not exist."}, status=404
            )

        if not student.check_password(password):
            return JsonResponse(
                {"success": False, "message": "Invalid password."}, status=401
            )

        request.session["username"] = student.username
        request.session["is_student_authenticated"] = True
        return JsonResponse(
            {
                "success": True,
                "message": "Signed in successfully.",
                "student_name": student.name,
                "greeting": True,
            },
            status=200,
        )

    elif mode == "signup":
        if Student.objects.filter(student_id=student_id).exists():
            return JsonResponse(
                {"success": False, "message": "Student ID already exists."}, status=400
            )

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        phone_number = data.get("phone_number", "").strip()

        if not all([name, email, phone_number]):
            return JsonResponse(
                {"success": False, "message": "All fields are required."}, status=400
            )

        # Optional: Email validation
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse(
                {"success": False, "message": "Invalid email address."}, status=400
            )

        # Optional: Add phone number format validation here if needed

        student = Student(
            student_id=student_id,
            name=name,
            email=email,
            phone_number=phone_number,
        )
        student.set_password(password)
        student.save()

        request.session["username"] = student.username
        request.session["is_student_authenticated"] = True
        request.session.set_expiry(3600)
        return JsonResponse(
            {
                "success": True,
                "message": "Signed up and logged in.",
                "student_name": name,
                "greeting": False,
            },
            status=201,
        )

    else:
        return JsonResponse({"success": False, "message": "Invalid mode."}, status=400)


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
