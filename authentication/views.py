import json
from django.core.validators import validate_email
from django.db import models
from django.forms import ValidationError
from django.views.decorators.csrf import csrf_exempt
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import sys, os
from authentication.models import Preference, Student


def auth(request):
    return render(request, "authentication/authentication.html")


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
        {"student": student, "total_searches": total_searches},
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

        request.session["student_id"] = student.student_id
        request.session["is_student_authenticated"] = True
        request.session.set_expiry(3600)  # session expires in 1 hour

        return JsonResponse(
            {"success": True, "message": "Signed in successfully."}, status=200
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


@csrf_exempt
def delete_history(request, id):
    if request.method == "DELETE":
        Preference.objects.filter(id=id).delete()
        return JsonResponse({"status": "deleted"})
    return JsonResponse({"error": "Invalid method"}, status=405)
