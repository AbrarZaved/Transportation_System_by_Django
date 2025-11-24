from rest_framework import serializers
from .models import TripInstance, Transportation_schedules
from transit_hub.models import Bus, Driver, Route


class ScheduleBasicSerializer(serializers.ModelSerializer):
    """Basic schedule serializer for nested usage"""

    route_name = serializers.CharField(source="route.route_name", read_only=True)
    bus_name = serializers.CharField(source="bus.bus_name", read_only=True)
    bus_tag = serializers.CharField(source="bus.bus_tag", read_only=True)
    driver_name = serializers.CharField(source="driver.name", read_only=True)

    class Meta:
        model = Transportation_schedules
        fields = [
            "schedule_id",
            "route_name",
            "bus_name",
            "bus_tag",
            "driver_name",
            "departure_time",
            "estimated_end_time",
            "from_dsc",
            "to_dsc",
            "audience",
        ]


class TripInstanceSerializer(serializers.ModelSerializer):
    """Serializer for TripInstance model"""

    schedule_info = ScheduleBasicSerializer(source="schedule", read_only=True)
    is_today = serializers.BooleanField(read_only=True)
    can_start = serializers.BooleanField(read_only=True)
    can_complete = serializers.BooleanField(read_only=True)
    scheduled_start_datetime = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TripInstance
        fields = [
            "id",
            "schedule",
            "date",
            "status",
            "actual_start_time",
            "actual_end_time",
            "created_at",
            "updated_at",
            "schedule_info",
            "is_today",
            "can_start",
            "can_complete",
            "scheduled_start_datetime",
        ]
        read_only_fields = [
            "actual_start_time",
            "actual_end_time",
            "created_at",
            "updated_at",
        ]


class TripInstanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating trip instances"""

    class Meta:
        model = TripInstance
        fields = ["schedule", "date"]

    def validate(self, data):
        """Validate that schedule is active and no duplicate trip exists"""
        schedule = data["schedule"]
        date = data["date"]

        if not schedule.schedule_status:
            raise serializers.ValidationError("Schedule is not active")

        # Check if trip instance already exists for this date
        if TripInstance.objects.filter(schedule=schedule, date=date).exists():
            raise serializers.ValidationError(
                "Trip instance already exists for this date"
            )

        return data


class TodayTripsSerializer(serializers.ModelSerializer):
    """Serializer for today's trips view"""

    schedule_info = ScheduleBasicSerializer(source="schedule", read_only=True)
    is_overdue = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = TripInstance
        fields = [
            "id",
            "status",
            "actual_start_time",
            "actual_end_time",
            "schedule_info",
            "is_overdue",
            "duration_minutes",
        ]

    def get_is_overdue(self, obj):
        """Check if trip is overdue"""
        if obj.status == "pending":
            from django.utils import timezone
            import datetime

            now = timezone.now()
            scheduled_time = timezone.make_aware(
                datetime.datetime.combine(obj.date, obj.schedule.departure_time)
            )
            return now > scheduled_time
        return False

    def get_duration_minutes(self, obj):
        """Get trip duration in minutes if completed"""
        if obj.actual_start_time and obj.actual_end_time:
            duration = obj.actual_end_time - obj.actual_start_time
            return int(duration.total_seconds() / 60)
        return None


class DriverTripSerializer(serializers.ModelSerializer):
    """Serializer for driver's trip list"""

    schedule_id = serializers.IntegerField(source="schedule.schedule_id")
    route_name = serializers.CharField(source="schedule.route.route_name")
    bus_name = serializers.CharField(source="schedule.bus.bus_name")
    bus_tag = serializers.CharField(source="schedule.bus.bus_tag")
    departure_time = serializers.TimeField(source="schedule.departure_time")
    from_dsc = serializers.BooleanField(source="schedule.from_dsc")
    to_dsc = serializers.BooleanField(source="schedule.to_dsc")

    class Meta:
        model = TripInstance
        fields = [
            "id",
            "schedule_id",
            "route_name",
            "bus_name",
            "bus_tag",
            "departure_time",
            "from_dsc",
            "to_dsc",
            "status",
            "can_start",
            "can_complete",
        ]
