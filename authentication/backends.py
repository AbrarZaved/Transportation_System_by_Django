# backends.py
from django.contrib.auth.backends import BaseBackend
from .models import Student


class StudentAuthBackend(BaseBackend):
    def authenticate(self, request, student_id=None, password=None):
        try:
            student = Student.objects.get(student_id=student_id)
            if student.check_password(password):
                return student
        except Student.DoesNotExist:
            return None

    def get_user(self, student_id):
        try:
            return Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return None
