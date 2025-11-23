from django.contrib import admin

from transit_hub.models import (
    Bus,
    Driver,
    Helper,
    Route,
    RouteStoppage,
    Stoppage,
    Notice,
)

# Register your models here.


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "phone_number",
        "license_number",
        "license_expiry",
        "license_class",
        "license_country",
        "license_issued",
        "driver_status",
        "created_at",
        "updated_at",
    ]
    list_filter = ["driver_status", "created_at", "updated_at"]
    search_fields = [
        "name",
        "phone_number",
        "license_number",
        "license_class",
        "license_country",
    ]
    list_per_page = 100


@admin.register(Helper)
class HelperAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "phone_number",
        "helper_status",
        "created_at",
        "updated_at",
    ]
    list_filter = ["helper_status", "created_at", "updated_at"]
    search_fields = [
        "name",
        "phone_number",
    ]
    list_per_page = 100


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = [
        "bus_name",
        "bus_number",
        "bus_model",
        "bus_capacity",
        "bus_status",
        "created_at",
        "updated_at",
    ]
    list_filter = ["bus_status", "created_at", "updated_at"]
    search_fields = ["bus_name", "bus_number", "bus_model"]
    list_per_page = 100


class RouteStoppageInline(admin.TabularInline):
    model = RouteStoppage
    extra = 1  # ✅ Show one extra row for adding new stoppages
    fields = ["stoppage"]  # ✅ Select stoppage and define order


admin.site.register(RouteStoppage)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = [
        "route_name",
        "route_number",
        "route_status",
        "from_dsc",
        "to_dsc",
        "created_at",
        "updated_at",
    ]
    search_fields = ["route_name", "route_number"]
    list_filter = ["route_status", "from_dsc", "to_dsc", "created_at", "updated_at"]
    inlines = [RouteStoppageInline]  # ✅ Inline stoppages inside Route

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).order_by("created_at")


@admin.register(Stoppage)
class StoppageAdmin(admin.ModelAdmin):
    list_display = ["stoppage_name", "stoppage_status", "created_at", "updated_at"]
    search_fields = ["stoppage_name"]


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "notice_type",
        "route",
        "is_active",
        "created_at",
        "expires_at",
    ]
    list_filter = ["notice_type", "is_active", "created_at", "route"]
    search_fields = ["title", "message"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Notice Information", {"fields": ("title", "message", "notice_type")}),
        (
            "Targeting",
            {
                "fields": ("route",),
                "description": "Leave route empty for global notice that shows on all routes",
            },
        ),
        ("Status & Timing", {"fields": ("is_active", "expires_at")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("route")
