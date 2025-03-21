from django.contrib import admin

from transit_hub.models import Bus, Driver, Route, RouteStoppage, Stoppage

# Register your models here.


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
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
        "first_name",
        "last_name",
        "phone_number",
        "license_number",
        "license_class",
        "license_country",
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

    def get_queryset(self,*args, **kwargs):
        return super().get_queryset(*args, **kwargs).order_by('created_at')

@admin.register(Stoppage)
class StoppageAdmin(admin.ModelAdmin):
    list_display = ["stoppage_name", "stoppage_status", "created_at", "updated_at"]
    search_fields = ["stoppage_name"]
