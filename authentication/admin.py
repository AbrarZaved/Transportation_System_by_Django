from django.contrib import admin
from django.contrib.auth.models import Group as groups
from authentication.models import (
    DriverAuth,
    EmailOTP,
    Preference,
    Student,
    Supervisor,
    StudentReview,
    SupportTicket,
    TicketMessage,
    StudentLoginActivity,
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


@admin.register(StudentReview)
class StudentReviewAdmin(admin.ModelAdmin):
    list_display = ["student", "get_target", "rating", "is_approved", "created_at"]
    list_filter = ["rating", "is_approved", "created_at"]
    search_fields = [
        "student__name",
        "student__student_id",
        "comment",
        "bus__bus_name",
        "driver__name",
    ]
    readonly_fields = ["created_at", "updated_at"]
    list_editable = ["is_approved"]

    def get_target(self, obj):
        if obj.bus:
            return f"Bus: {obj.bus.bus_name}"
        elif obj.driver:
            return f"Driver: {obj.driver.name}"
        return "No target"

    get_target.short_description = "Target"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("student", "bus", "driver").order_by("-created_at")


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = [
        "ticket_id",
        "student",
        "subject",
        "category",
        "status",
        "assigned_to",
        "created_at",
    ]
    list_filter = ["status", "category", "created_at"]
    search_fields = [
        "ticket_id",
        "student__name",
        "student__student_id",
        "subject",
        "description",
    ]
    readonly_fields = ["ticket_id", "created_at", "updated_at", "resolved_at"]
    list_editable = ["status"]

    fieldsets = (
        (
            "Ticket Information",
            {"fields": ("ticket_id", "student", "subject", "category", "description")},
        ),
        ("Status & Priority", {"fields": ("status", "priority", "assigned_to")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "resolved_at")}),
    )


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ["ticket", "get_sender", "is_internal", "created_at"]
    list_filter = ["is_internal", "created_at"]
    search_fields = ["ticket__ticket_id", "message"]
    readonly_fields = ["created_at"]

    def get_sender(self, obj):
        if obj.sender_student:
            return f"Student: {obj.sender_student.name}"
        elif obj.sender_supervisor:
            return f"Admin: {obj.sender_supervisor.first_name} {obj.sender_supervisor.last_name}"
        return "Unknown"

    get_sender.short_description = "Sender"


@admin.register(StudentLoginActivity)
class StudentLoginActivityAdmin(admin.ModelAdmin):
    list_display = ["student", "login_time", "location", "ip_address"]
    list_filter = ["login_time"]
    search_fields = ["student__name", "student__student_id", "ip_address", "location"]
    readonly_fields = ["login_time"]
    date_hierarchy = "login_time"
