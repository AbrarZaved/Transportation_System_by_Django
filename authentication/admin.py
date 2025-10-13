from django.contrib import admin
from django.contrib.auth.models import Group as groups

from authentication.models import EmailOTP, Preference, Student, Supervisor

# Register your models here.
admin.site.unregister(groups)


@admin.register(Supervisor)
class SuperVisorAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "first_name", "last_name", "phone_number", "email"]
    search_fields = ["employee_id", "phone_number", "email"]
    list_filter = ["is_active", "is_staff", "is_admin", "is_superuser"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["student_id", "dept_name"]
    search_fields = ["student_id"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by("student_id")


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ["student", "searched_locations", "total_searches"]
    search_fields = ["student__student_id", "student__name"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by("student__student_id")


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ["user", "otp", "expires_at"]
    search_fields = ["user__email", "otp"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by("user__email")
