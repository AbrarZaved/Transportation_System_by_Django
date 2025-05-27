from django.contrib import admin
from django.contrib.auth.models import Group as groups

from authentication.models import Student, Supervisor

# Register your models here.
admin.site.unregister(groups)


@admin.register(Supervisor)
class SuperVisorAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "first_name", "last_name", "phone_number", "email"]
    search_fields = ["employee_id", "phone_number", "email"]
    list_filter = ["is_active", "is_staff", "is_admin", "is_superuser"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["student_id", "dept_name", "semester_enrolled"]
    search_fields = ["student_id"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by("student_id")
