from django.contrib import admin
from django.contrib.auth.models import Group as groups

from authentication.models import Supervisor

# Register your models here.
admin.site.unregister(groups)


@admin.register(Supervisor)
class SuperVisorAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "first_name", "last_name", "phone_number", "email"]
    search_fields = ["employee_id", "phone_number", "email"]
    list_filter = ["is_active", "is_staff", "is_admin", "is_superuser"]
