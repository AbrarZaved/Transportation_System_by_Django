import json
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.db import models
from django.forms import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import sys, os
from authentication.models import Preference, Student



# Create your views here.
def my_account(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("index")

    student = get_object_or_404(Student, student_id=student_id)
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

        request.session["student_id"] = student_id
        request.session["is_student_authenticated"] = True
        return JsonResponse(
            {"success": True, "message": "Signed in successfully.", "student_name": student.name}, status=200
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

        request.session["student_id"] = student.student_id
        request.session["is_student_authenticated"] = True
        request.session.set_expiry(3600)
        return JsonResponse(
            {"success": True, "message": "Signed up and logged in."}, status=201
        )

    else:
        return JsonResponse({"success": False, "message": "Invalid mode."}, status=400)


def sign_out(request):
    request.session.flush()
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
        student_id = request.POST.get("student_id")
        full_name = request.POST.get("full_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        dept_name = request.POST.get("dept_name", "").strip()
        batch_code = request.POST.get("batch_code", "").strip()

        student = get_object_or_404(Student, student_id=student_id)

        student.name = full_name
        student.phone_number = phone_number
        student.dept_name = dept_name
        student.batch_code = batch_code
        student.save()

        messages.success(request, "Your profile has been updated successfully.")
        return redirect("my_account")
