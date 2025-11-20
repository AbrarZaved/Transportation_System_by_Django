import datetime
from django.db import models
from multiselectfield import MultiSelectField
from transit_hub.models import Bus, Driver, Helper, Route
from datetime import timedelta


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
        ('fixed_route','Fixed Route'),
    ]

    schedule_id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.DO_NOTHING)
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPES, default="one_time")
    bus = models.ForeignKey(Bus, on_delete=models.DO_NOTHING)
    driver = models.ForeignKey(Driver, on_delete=models.DO_NOTHING)
    helper=models.ForeignKey(Helper,on_delete=models.DO_NOTHING,null=True,blank=True)
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

    class Meta:
        unique_together = ["schedule_id", "route", "bus", "driver"]
        verbose_name_plural = "Transportation Schedules"

    def save(self, *args, **kwargs):
        if self.departure_time:
            if not self.estimated_end_time:
                dt = datetime.datetime.combine(
                    datetime.date.today(), self.departure_time
                )
                dt += timedelta(hours=3)
                self.estimated_end_time = dt.time()
        if self.schedule_status:
            self.bus.route_assigned = True
            self.bus.save()
            self.driver.bus_assigned = True
            self.driver.save()
        super(Transportation_schedules, self).save(*args, **kwargs)
