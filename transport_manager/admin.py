from django.contrib import admin

from transport_manager.models import LocationData, Transportation_schedules

# Register your models here.


@admin.register(Transportation_schedules)
class Transportation_schedulesAdmin(admin.ModelAdmin):
    list_display = [
        "schedule_id",
        "route",
        "bus",
        "driver",
        "departure_time",
        "schedule_status",
        "created_at",
    ]
    list_filter = ["route", "bus", "driver", "schedule_status", "from_dsc", "to_dsc"]
    search_fields = ["route", "bus", "driver", "schedule_status"]
    list_per_page = 100

@admin.register(LocationData)
class LocationDataAdmin(admin.ModelAdmin):
    list_display = ["bus", "latitude", "longitude", "timestamp"]
    list_filter = ["bus", "timestamp"]
    search_fields = ["bus__bus_name"]
    list_per_page = 100