from django.core.management.base import BaseCommand
from transport_manager.tasks import generate_daily_trip_instances
from datetime import date


class Command(BaseCommand):
    help = "Manually generate trip instances for today"

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Generate for specific date (YYYY-MM-DD format). Default is today.",
        )

    def handle(self, *args, **options):
        target_date = options.get("date")

        if target_date:
            try:
                # Parse the date
                from datetime import datetime

                target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                self.stdout.write(f"Generating trip instances for {target_date}...")

                # Temporarily modify the task to use the specified date
                from transport_manager.models import (
                    Transportation_schedules,
                    TripInstance,
                )

                current_day = target_date.strftime("%A").lower()

                active_schedules = Transportation_schedules.objects.filter(
                    schedule_status=True, days__contains=current_day
                ).select_related("route", "bus", "driver")

                created_count = 0
                for schedule in active_schedules:
                    trip_instance, created = TripInstance.objects.get_or_create(
                        schedule=schedule,
                        date=target_date,
                        defaults={"status": "pending"},
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(
                            f"✓ Created trip for {schedule.route.route_name}"
                        )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created {created_count} trip instances for {target_date}"
                    )
                )

            except ValueError:
                self.stdout.write(
                    self.style.ERROR("Invalid date format. Use YYYY-MM-DD format.")
                )
        else:
            # Generate for today
            self.stdout.write(
                f"Generating trip instances for today ({date.today()})..."
            )
            result = generate_daily_trip_instances()

            self.stdout.write(f'Created: {result["created_count"]} trips')
            self.stdout.write(f'Skipped: {result["skipped_count"]} trips')

            if result["errors"]:
                self.stdout.write(
                    self.style.WARNING(f'Errors: {len(result["errors"])}')
                )
                for error in result["errors"]:
                    self.stdout.write(f"  - {error}")
            else:
                self.stdout.write(self.style.SUCCESS("No errors occurred!"))
