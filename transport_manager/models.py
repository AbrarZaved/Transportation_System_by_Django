import datetime
import os
from django.contrib.auth.hashers import make_password
from django.db import models, transaction
from django.utils import timezone
from multiselectfield import MultiSelectField
from transit_hub.models import Bus, Driver, Helper, Route
from datetime import timedelta, date


class Transportation_schedules(models.Model):

    audiences = [
        ("employee", "Employees"),
        ("student", "Students"),
        ("female_only", "Female Only"),
    ]

    DAYS_CHOICES = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    ]
    TRIP_TYPES = [
        ("one_time", "One Time"),
        ("fixed_route", "Fixed Route"),
    ]

    schedule_id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.DO_NOTHING)
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPES, default="one_time")
    bus = models.ForeignKey(Bus, on_delete=models.DO_NOTHING)
    driver = models.ForeignKey(Driver, on_delete=models.DO_NOTHING)
    helper = models.ForeignKey(
        Helper, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    audience = models.CharField(max_length=20, choices=audiences, default="student")

    # Changed from JSONField to MultiSelectField
    days = MultiSelectField(
        choices=DAYS_CHOICES,
        help_text="Select multiple days",
        default=["monday", "tuesday", "wednesday", "thursday", "saturday", "sunday"],
    )

    departure_time = models.TimeField()
    estimated_end_time = models.TimeField(null=True, blank=True)
    schedule_status = models.BooleanField()
    from_dsc = models.BooleanField(default=False)
    to_dsc = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Schedule {self.route.route_name}"
    class Meta:
        unique_together = ["schedule_id", "route", "bus", "driver"]
        verbose_name_plural = "Transportation Schedules"

    def save(self, *args, **kwargs):
        # Only calculate estimated end time, remove assignment logic
        if self.departure_time and not self.estimated_end_time:
            dt = datetime.datetime.combine(datetime.date.today(), self.departure_time)
            dt += timedelta(hours=3)
            self.estimated_end_time = dt.time()
        super(Transportation_schedules, self).save(*args, **kwargs)

    def is_active_today(self):
        """Check if this schedule should run today"""
        current_day = timezone.localtime().strftime("%A").lower()
        return current_day in self.days and self.schedule_status

    def get_today_trip_instance(self):
        """Get today's trip instance for this schedule"""
        today = date.today()
        try:
            return self.trip_instances.get(date=today)
        except TripInstance.DoesNotExist:
            return None


class TripInstance(models.Model):
    """Represents a single execution of a schedule for a specific date"""

    TRIP_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    schedule = models.ForeignKey(
        Transportation_schedules,
        on_delete=models.CASCADE,
        related_name="trip_instances",
    )
    date = models.DateField()
    status = models.CharField(
        max_length=20, choices=TRIP_STATUS_CHOICES, default="pending"
    )

    # Actual trip times
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)

    # Additional tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("schedule", "date")
        ordering = ["-date", "schedule__departure_time"]
        verbose_name_plural = "Trip Instances"

    def __str__(self):
        return f"{self.schedule.route.route_name} - {self.date} - {self.status}"

    @property
    def is_today(self):
        return self.date == date.today()

    @property
    def scheduled_start_datetime(self):
        """Get the scheduled start datetime for this trip"""
        return datetime.datetime.combine(self.date, self.schedule.departure_time)

    @property
    def can_start(self):
        """Check if trip can be started"""
        now = timezone.now()
        scheduled_time = timezone.make_aware(
            datetime.datetime.combine(self.date, self.schedule.departure_time)
        )
        # Allow starting 15 minutes before scheduled time
        return self.status == "pending" and now >= (
            scheduled_time - timedelta(minutes=15)
        )

    @property
    def can_complete(self):
        """Check if trip can be completed"""
        return self.status == "in_progress"

    def start_trip(self):
        """Start the trip and assign resources"""
        if not self.can_start:
            raise ValueError("Trip cannot be started at this time")

        with transaction.atomic():
            # Update trip status
            self.status = "in_progress"
            self.actual_start_time = timezone.now()
            self.save()

            # Assign resources
            self.schedule.bus.route_assigned = True
            self.schedule.bus.save(update_fields=["route_assigned"])

            # Update driver statistics
            driver = self.schedule.driver
            driver.total_trip_assigned += 1
            driver.save(update_fields=["total_trip_assigned"])

    def complete_trip(self):
        """Complete the trip and free up resources"""
        if not self.can_complete:
            raise ValueError("Trip is not in progress")

        with transaction.atomic():
            # Update trip status
            self.status = "completed"
            self.actual_end_time = timezone.now()
            self.save()

            # Free up resources
            self.schedule.bus.route_assigned = False
            self.schedule.bus.save(update_fields=["route_assigned"])

            # Update driver statistics
            driver = self.schedule.driver
            driver.total_trip_completed += 1
            driver.total_trip_assigned -= 1
            driver.save(update_fields=["total_trip_completed", "total_trip_assigned"])

    def cancel_trip(self, reason=""):
        """Cancel the trip"""
        if self.status == "completed":
            raise ValueError("Cannot cancel completed trip")

        with transaction.atomic():
            # If trip was in progress, free up resources
            if self.status == "in_progress":
                self.schedule.bus.route_assigned = False
                self.schedule.bus.save(update_fields=["route_assigned"])

                driver = self.schedule.driver
                driver.total_trip_assigned -= 1
                driver.save(update_fields=["total_trip_assigned"])

            self.status = "cancelled"
            self.save()

    def reset_trip(self):
        """Reset trip to pending status (admin function)"""
        if self.status == "in_progress":
            # Free up resources first
            self.schedule.bus.route_assigned = False
            self.schedule.bus.save(update_fields=["route_assigned"])

            driver = self.schedule.driver
            driver.total_trip_assigned -= 1
            driver.save(update_fields=["total_trip_assigned"])

        self.status = "pending"
        self.actual_start_time = None
        self.actual_end_time = None
        self.save()


class LocationData(models.Model):
    """Bus location tracking model"""

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"LocationData for {self.bus.bus_name} at {self.timestamp}"
