from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Driver(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
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

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        unique_together = ["phone_number", "license_number"]


class Bus(models.Model):
    bus_name = models.CharField(max_length=100)
    bus_number = models.CharField(max_length=30)
    bus_model = models.CharField(max_length=30)
    bus_capacity = models.IntegerField()
    bus_photo = models.ImageField(upload_to="bus_photos")
    bus_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bus_name + " " + str(self.bus_number)

    class Meta:
        verbose_name_plural = "Buses"
        unique_together = ["bus_name", "bus_number"]


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
        return self.route_name + " " + str(self.route_number)

    class Meta:
        unique_together = ["route_name", "route_number"]

    def save(self, *args, **kwargs):
        route_name = str(self.route_name[:3])
        if route_name == "DSC":
            self.from_dsc = True
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
