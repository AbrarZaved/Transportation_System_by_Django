import os
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import check_password, make_password

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.text import slugify
from django.utils.timezone import now
import uuid

from transit_hub.models import Driver


class SuperVisorManager(BaseUserManager):
    def create_user(self, employee_id, password=None, **extra_fields):
        if not employee_id:
            raise ValueError("Users must have an employee_id")

        user = self.model(employee_id=employee_id, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_admin"):
            raise ValueError("Superuser must have is_admin=True.")
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(employee_id, password, **extra_fields)


# Create your models here.
class Supervisor(AbstractBaseUser):
    employee_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=90)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    username = None
    groups = None

    USERNAME_FIELD = "employee_id"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    objects = SuperVisorManager()


class Student(models.Model):
    name = models.CharField(max_length=50)
    profile_pic = models.ImageField(
        upload_to="student_profiles/", default="meerkat.png"
    )
    student_id = models.CharField(max_length=20, unique=True)
    dept_name = models.CharField(max_length=50)
    batch_code = models.CharField(max_length=5)
    phone_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=90, unique=True)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=50, null=True, blank=True)
    verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = f"{slugify(self.name)}-{uuid.uuid4().hex[:4]}"
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name


class EmailOTP(models.Model):
    user = models.ForeignKey(Student, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return now() > self.expires_at

    def __str__(self):
        return f"EmailOTP for {self.user.email}"


class Preference(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    searched_locations = models.CharField(max_length=100, blank=True, null=True)
    total_searches = models.IntegerField(default=0)
    last_searched = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.searched_locations:
            self.searched_locations = (
                self.searched_locations.capitalize()
            )  # Make the first letter upper case
        super().save(*args, **kwargs)


class StudentReview(models.Model):
    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    bus = models.ForeignKey(
        "transit_hub.Bus", on_delete=models.CASCADE, null=True, blank=True
    )
    driver = models.ForeignKey(
        "transit_hub.Driver", on_delete=models.CASCADE, null=True, blank=True
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)  # Auto-approved as per requirement

    class Meta:
        unique_together = [
            "student",
            "bus",
            "driver",
        ]  # One review per student per bus-driver combination
        ordering = ["-created_at"]
        db_table = "authentication_studentreview"

    def __str__(self):
        targets = []
        if self.bus:
            targets.append(f"Bus: {self.bus.bus_name}")
        if self.driver:
            targets.append(f"Driver: {self.driver.name}")
        target = " & ".join(targets) if targets else "No target"
        return f"{self.student.name} - {target} - {self.rating} stars"

    def save(self, *args, **kwargs):
        # Ensure at least bus or driver is provided
        if not self.bus and not self.driver:
            raise ValueError("At least bus or driver must be provided")
        super().save(*args, **kwargs)


class DriverAuth(models.Model):
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    auth_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Auth for {self.driver.name}"

    def save(self, *args, **kwargs):
        if self.pk is None or (
            hasattr(self, "_password_changed") and self._password_changed
        ):
            # Check if password is already hashed
            if not self.password.startswith(("pbkdf2_", "bcrypt", "argon2")):
                self.password = make_password(self.password)

        if not self.username:
            name = self.driver.name.lower().replace(" ", "_")
            self.username = f"{name}_{self.driver.id}"
        if not self.auth_token:
            self.auth_token = os.urandom(24).hex()
        super(DriverAuth, self).save(*args, **kwargs)

    def set_password(self, raw_password):
        """Set password and mark it as changed"""
        self.password = raw_password
        self._password_changed = True

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
