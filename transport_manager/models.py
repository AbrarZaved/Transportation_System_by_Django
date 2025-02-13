from django.db import models
from transit_hub.models import Bus, Driver, Route


class Transportation_schedules(models.Model):

    audiences = [
        ("employee", "Employees"),
        ("student", "Students"),
        ("female_only", "Female Only"),
    ]

    schedule_id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.DO_NOTHING)
    bus = models.ForeignKey(Bus, on_delete=models.DO_NOTHING)
    driver = models.ForeignKey(Driver, on_delete=models.DO_NOTHING)
    audience = models.CharField(max_length=20, choices=audiences, default="student")
    departure_time = models.DateTimeField()
    schedule_status = models.BooleanField()
    from_dsc = models.BooleanField(default=False)
    to_dsc = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["schedule_id", "route", "bus", "driver"]
        verbose_name_plural = "Transportation Schedules"
