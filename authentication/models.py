from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import check_password, make_password

from django.db import models
from django.contrib.auth.models import AbstractBaseUser


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

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    objects = SuperVisorManager()


class Student(models.Model):
    name = models.CharField(max_length=50)
    student_id = models.CharField(max_length=20, unique=True)
    dept_name = models.CharField(max_length=50)
    batch_code = models.CharField(max_length=5, default="221")
    phone_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=90, unique=True)
    password = models.CharField(max_length=128)  # hashed password

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name


class Preference(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    searched_locations = models.CharField(max_length=100, blank=True, null=True)
    total_searches = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
