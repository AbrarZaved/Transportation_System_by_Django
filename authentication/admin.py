from django.contrib import admin
from django.contrib.auth.models import Group as groups
from authentication.models import (
    DriverAuth,
    EmailOTP,
    Preference,
    Student,
    Supervisor,
    Review,
)


admin.site.unregister(groups)


@admin.register(Supervisor)
class SuperVisorAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "first_name", "last_name", "phone_number", "email"]
    search_fields = ["employee_id", "phone_number", "email"]
    list_filter = ["is_active", "is_staff", "is_admin", "is_superuser"]


@admin.register(DriverAuth)
class DriverAuthAdmin(admin.ModelAdmin):
    list_display = ["username", "auth_token", "device_id", "created_at", "updated_at"]
    search_fields = ["username", "auth_token", "device_id"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["student_id", "username", "dept_name"]
    search_fields = ["student_id", "username"]

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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["student", "get_target", "rating", "is_approved", "created_at"]
    list_filter = ["rating", "is_approved", "created_at"]
    search_fields = [
        "student__name",
        "student__student_id",
        "comment",
        "bus__bus_name",
        "route__route_name",
    ]
    readonly_fields = ["created_at", "updated_at"]
    list_editable = ["is_approved"]

    def get_target(self, obj):
        if obj.bus:
            return f"Bus: {obj.bus.bus_name}"
        elif obj.route:
            return f"Route: {obj.route.route_name}"
        return "No target"

    get_target.short_description = "Target"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("student", "bus", "route").order_by("-created_at")
