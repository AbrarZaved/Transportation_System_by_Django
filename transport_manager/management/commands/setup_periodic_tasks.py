from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):
    help = "Setup periodic tasks for the transportation system"

    def handle(self, *args, **options):
        self.stdout.write("Setting up periodic tasks...")

        # Create crontab schedules

        # Daily at midnight for trip instance generation
        midnight_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=0,
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        # Every 6 hours for overdue trip cleanup
        every_6_hours, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour="*/6",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        # Daily at 11:30 PM for resetting assignments
        late_night_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=30,
            hour=23,
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        # Weekly cleanup on Sundays at 2 AM
        weekly_schedule, created = CrontabSchedule.objects.get_or_create(
            minute=0,
            hour=2,
            day_of_week=0,  # Sunday
            day_of_month="*",
            month_of_year="*",
        )

        # Create periodic tasks

        # 1. Generate daily trip instances
        task1, created = PeriodicTask.objects.get_or_create(
            crontab=midnight_schedule,
            name="Generate Daily Trip Instances",
            defaults={
                "task": "transport_manager.tasks.generate_daily_trip_instances",
                "enabled": True,
            },
        )
        if created:
            self.stdout.write(f"✓ Created task: {task1.name}")
        else:
            self.stdout.write(f"✓ Task already exists: {task1.name}")

        # 2. Auto-complete overdue trips
        task2, created = PeriodicTask.objects.get_or_create(
            crontab=every_6_hours,
            name="Auto Complete Overdue Trips",
            defaults={
                "task": "transport_manager.tasks.auto_complete_overdue_trips",
                "enabled": True,
            },
        )
        if created:
            self.stdout.write(f"✓ Created task: {task2.name}")
        else:
            self.stdout.write(f"✓ Task already exists: {task2.name}")

        # 3. Reset daily assignments
        task3, created = PeriodicTask.objects.get_or_create(
            crontab=late_night_schedule,
            name="Reset Daily Assignments",
            defaults={
                "task": "transport_manager.tasks.reset_daily_assignments",
                "enabled": True,
            },
        )
        if created:
            self.stdout.write(f"✓ Created task: {task3.name}")
        else:
            self.stdout.write(f"✓ Task already exists: {task3.name}")

        # 4. Weekly cleanup of old trip instances
        task4, created = PeriodicTask.objects.get_or_create(
            crontab=weekly_schedule,
            name="Cleanup Old Trip Instances",
            defaults={
                "task": "transport_manager.tasks.cleanup_old_trip_instances",
                "enabled": True,
            },
        )
        if created:
            self.stdout.write(f"✓ Created task: {task4.name}")
        else:
            self.stdout.write(f"✓ Task already exists: {task4.name}")

        self.stdout.write(self.style.SUCCESS("Successfully set up periodic tasks!"))
        self.stdout.write("")
        self.stdout.write("Scheduled tasks:")
        self.stdout.write("• Daily at 00:00: Generate trip instances for today")
        self.stdout.write("• Every 6 hours: Auto-complete overdue trips")
        self.stdout.write("• Daily at 23:30: Reset bus/driver assignments")
        self.stdout.write("• Weekly on Sunday 02:00: Cleanup old trip instances")
