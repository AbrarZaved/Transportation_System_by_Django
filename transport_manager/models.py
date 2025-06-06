from django.db import models
from multiselectfield import MultiSelectField
from transit_hub.models import Bus, Driver, Route


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

    schedule_id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.DO_NOTHING)
    bus = models.ForeignKey(Bus, on_delete=models.DO_NOTHING)
    driver = models.ForeignKey(Driver, on_delete=models.DO_NOTHING)
    audience = models.CharField(max_length=20, choices=audiences, default="student")

    # Changed from JSONField to MultiSelectField
    days = MultiSelectField(
        choices=DAYS_CHOICES,
        help_text="Select multiple days",
    )

    departure_time = models.TimeField()
    schedule_status = models.BooleanField()
    from_dsc = models.BooleanField(default=False)
    to_dsc = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["schedule_id", "route", "bus", "driver"]
        verbose_name_plural = "Transportation Schedules"
