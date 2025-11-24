from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from transport_manager.models import (
    LocationData,
    Transportation_schedules,
    TripInstance,
)

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
        "trip_instances_count",
        "created_at",
    ]
    list_filter = [
        "route",
        "bus",
        "driver",
        "schedule_status",
        "from_dsc",
        "to_dsc",
        "days",
    ]
    search_fields = ["route__route_name", "bus__bus_name", "driver__name"]
    list_per_page = 100
    readonly_fields = ["trip_instances_count"]

    def trip_instances_count(self, obj):
        count = obj.trip_instances.count()
        return count

    trip_instances_count.short_description = "Trip Instances"


@admin.register(TripInstance)
class TripInstanceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "schedule_info",
        "date",
        "status",
        "actual_start_time",
        "actual_end_time",
        "is_overdue",
        "action_buttons",
    ]
    list_filter = [
        "status",
        "date",
        "schedule__route",
        "schedule__bus",
        "schedule__driver",
    ]
    search_fields = [
        "schedule__route__route_name",
        "schedule__bus__bus_name",
        "schedule__driver__name",
    ]
    date_hierarchy = "date"
    list_per_page = 50
    readonly_fields = [
        "scheduled_start_datetime",
        "is_today",
        "can_start",
        "can_complete",
        "created_at",
        "updated_at",
    ]

    def schedule_info(self, obj):
        return f"{obj.schedule.route.route_name} - {obj.schedule.bus.bus_tag}"

    schedule_info.short_description = "Schedule"

    def is_overdue(self, obj):
        if obj.status == "pending":
            now = timezone.now()
            scheduled_time = timezone.make_aware(
                timezone.datetime.combine(obj.date, obj.schedule.departure_time)
            )
            if now > scheduled_time:
                return format_html('<span style="color: red;">Yes</span>')
        return "No"

    is_overdue.short_description = "Overdue"

    def action_buttons(self, obj):
        if obj.status == "pending" and obj.can_start:
            return format_html('<button onclick="startTrip({})">Start</button>', obj.id)
        elif obj.status == "in_progress" and obj.can_complete:
            return format_html(
                '<button onclick="completeTrip({})">Complete</button>', obj.id
            )
        return "-"

    action_buttons.short_description = "Actions"

    actions = ["mark_pending", "mark_cancelled", "reset_trips"]

    def mark_pending(self, request, queryset):
        for trip in queryset:
            try:
                trip.reset_trip()
                self.message_user(request, f"Trip {trip} reset to pending")
            except Exception as e:
                self.message_user(
                    request, f"Error resetting trip {trip}: {e}", level="ERROR"
                )

    mark_pending.short_description = "Reset selected trips to pending"

    def mark_cancelled(self, request, queryset):
        for trip in queryset:
            try:
                trip.cancel_trip()
                self.message_user(request, f"Trip {trip} cancelled")
            except Exception as e:
                self.message_user(
                    request, f"Error cancelling trip {trip}: {e}", level="ERROR"
                )

    mark_cancelled.short_description = "Cancel selected trips"

    def reset_trips(self, request, queryset):
        for trip in queryset:
            try:
                trip.reset_trip()
            except Exception as e:
                self.message_user(
                    request, f"Error resetting trip {trip}: {e}", level="ERROR"
                )
        self.message_user(request, f"Reset {queryset.count()} trips")

    reset_trips.short_description = "Reset selected trips"


@admin.register(LocationData)
class LocationDataAdmin(admin.ModelAdmin):
    """Bus location tracking admin"""

    list_display = ["bus", "latitude", "longitude", "timestamp"]
    list_filter = ["bus", "timestamp"]
    search_fields = ["bus__bus_name"]
    list_per_page = 100
