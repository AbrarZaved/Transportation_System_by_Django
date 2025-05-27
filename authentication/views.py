import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from authentication.models import Student


# Create your views here.
def my_account(request):
    student_id = request.session.get("student_id")
    if not student_id:
        return redirect("index")

    student = get_object_or_404(Student, student_id=student_id)
    return render(request, "authentication/my_account.html", {"student": student})


def sign_in(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()

        if not student_id:
            return JsonResponse({"message": "Student ID is required"}, status=400)

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
        request.session.set_expiry(3600)  # 1 hour

        return render(request, "authentication/my_account.html", {"student": student})

    return JsonResponse({"message": "Invalid request method"}, status=405)


def sign_out(request):
    request.session.flush()
    return redirect("index")
