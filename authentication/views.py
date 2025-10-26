from email import message
import json
from functools import wraps
import re
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


def send_otp_view(user):
    otp = create_email_otp(user)
    send_otp_email(user, otp)
    return redirect("verify_otp")


def verify_otp_view(request):
    if request.method == "POST":
        otp_input = json.loads(request.body).get("otp")
        print(otp_input)
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


def login_request(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        password = request.POST.get("password", "").strip()
        student = Student.objects.filter(student_id=student_id).first()
        if student and student.check_password(password):
            request.session["username"] = student.username
            request.session["is_student_authenticated"] = True
            request.session.set_expiry(3600)  # 1 hour
            messages.success(request, "Logged in!", extra_tags=str(student.name))
            return redirect("index")


def register_request(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        password = request.POST.get("password", "").strip()
        if Student.objects.filter(student_id=student_id).exists():
            return JsonResponse(
                {"success": False, "message": "Student ID already exists."}, status=400
            )

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()

        # Optional: Email validation
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse(
                {"success": False, "message": "Invalid email address."}, status=400
            )

        student = Student(
            student_id=student_id,
            name=name,
            email=email,
            phone_number=phone_number,
        )
        student.set_password(password)
        student.save()
        otp_sent = send_otp_view(student)
        if otp_sent:
            messages.warning(request, "OTP Sent!")
            return redirect("verify_otp")
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
