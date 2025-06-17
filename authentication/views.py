import json
from django.db import models
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


def sign_in(request):
    if request.method == "POST":
        student_id = json.loads(request.body).get("student_id", "").strip()
        student = Student.objects.filter(student_id=student_id).first()
        if not student:
            try:
                response = requests.get(
                    f"http://peoplepulse.diu.edu.bd:8189/result/studentInfo?studentId={student_id}",
                    timeout=5,
                )
                profile = response.json()
                if not profile or profile.get("studentId") in [None, "", "null"]:
                    return JsonResponse(
                        {"message": "Student ID doesn't exist"}, status=404
                    )

                student = Student.objects.create(
                    student_id=profile["studentId"],
                    name=profile.get("studentName", ""),
                    dept_name=profile.get("departmentName", ""),
                    semester_enrolled=profile.get("semesterName", ""),
                )

            except requests.RequestException as e:
                return JsonResponse(
                    {"message": "External server error. Try again later."}, status=503
                )

        request.session["student_id"] = student.student_id
        request.session["is_student_authenticated"] = True
        request.session.modified = True
        request.session.set_expiry(3600)  # 1 hour

        return JsonResponse({"success": True}, status=200)

    return JsonResponse({"message": "Invalid request method"}, status=405)


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
