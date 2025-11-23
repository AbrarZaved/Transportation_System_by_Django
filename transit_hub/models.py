from os import name
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Driver(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=30)
    license_expiry = models.DateField()
    license_class = models.CharField(max_length=10)
    license_country = models.CharField(max_length=30)
    license_issued = models.DateField()
    license_photo = models.ImageField(upload_to="license_photos", null=True, blank=True)
    driver_photo = models.ImageField(upload_to="driver_photos", null=True, blank=True)
    driver_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_trip_assigned = models.IntegerField(default=0)
    total_trip_completed = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name)

    class Meta:
        unique_together = ["phone_number", "license_number"]


class Helper(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    helper_photo = models.ImageField(upload_to="helper_photos", null=True, blank=True)
    helper_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bus_assigned = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        unique_together = ["phone_number"]


class Bus(models.Model):
    bus_name = models.CharField(max_length=100)
    bus_tag = models.CharField(max_length=30, unique=True, null=True, blank=True)
    bus_number = models.CharField(max_length=30)
    bus_model = models.CharField(max_length=30)
    bus_capacity = models.IntegerField()
    bus_photo = models.ImageField(upload_to="bus_photos", null=True, blank=True)
    bus_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    route_assigned = models.BooleanField(default=False)

    def __str__(self):
        return self.bus_name

    def save(self, *args, **kwargs):
        if not self.bus_photo and "S" in self.bus_tag:
            self.bus_photo = "bus_photos/sunflower.jpg"
        if not self.bus_photo and "R" in self.bus_tag:
            self.bus_photo = "bus_photos/tuberose.jpg"
        super(Bus, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Buses"
        unique_together = ["bus_name", "bus_number", "bus_tag"]


class Stoppage(models.Model):
    stoppage_name = models.CharField(max_length=100, unique=True)
    stoppage_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.stoppage_name


class Route(models.Model):
    route_name = models.CharField(max_length=100)
    route_number = models.CharField(max_length=30)
    route_status = models.BooleanField(default=True)
    from_dsc = models.BooleanField(default=False, verbose_name="From DSC")
    to_dsc = models.BooleanField(default=False, verbose_name="To DSC")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.route_name

    class Meta:
        unique_together = ["route_name", "route_number"]

    def save(self, *args, **kwargs):
        route_name = str(self.route_name[:3])
        if route_name == "DSC":
            self.from_dsc = True
        else:
            self.to_dsc = True
        if self.from_dsc:
            self.to_dsc = False
        else:
            self.to_dsc = True
        return super(Route, self).save(*args, **kwargs)


class RouteStoppage(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    stoppage = models.ForeignKey(Stoppage, on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True
    )  # ✅ This keeps track of Stoppage 1, 2, 3, etc.
    objects = models.Manager()

    class Meta:  # ✅ Prevent duplicate order numbers for the same route
        ordering = ["-created_at"]  # ✅ Always show stoppages in order

    def __str__(self):
        return f"{self.route} - Stoppage {self.stoppage}"


class Notice(models.Model):
    NOTICE_TYPES = [
        ("info", "Information"),
        ("warning", "Warning"),
        ("urgent", "Urgent"),
        ("maintenance", "Maintenance"),
    ]

    title = models.CharField(max_length=200, help_text="Short title for the notice")
    message = models.TextField(help_text="Notice message content")
    notice_type = models.CharField(max_length=20, choices=NOTICE_TYPES, default="info")
    is_active = models.BooleanField(
        default=True, help_text="Whether this notice should be displayed"
    )
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Leave empty for global notice, or select specific route",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        blank=True, null=True, help_text="Notice will auto-hide after this time"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notice"
        verbose_name_plural = "Notices"

    def __str__(self):
        route_name = f" ({self.route.route_name})" if self.route else " (Global)"
        return f"{self.title}{route_name}"

    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone

            return timezone.now() > self.expires_at
        return False

    @property
    def is_visible(self):
        return self.is_active and not self.is_expired
