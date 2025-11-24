from django.core.management.base import BaseCommand
from transport_manager.models import TripInstance
from datetime import date


class Command(BaseCommand):
    help = "Test trip management functions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--list",
            action="store_true",
            help="List today's trip instances",
        )
        parser.add_argument(
            "--start",
            type=int,
            help="Start trip instance by ID",
        )
        parser.add_argument(
            "--complete",
            type=int,
            help="Complete trip instance by ID",
        )

    def handle(self, *args, **options):
        if options.get("list"):
            self.list_trips()
        elif options.get("start"):
            self.start_trip(options["start"])
        elif options.get("complete"):
            self.complete_trip(options["complete"])
        else:
            self.stdout.write("Use --list, --start ID, or --complete ID")

    def list_trips(self):
        today = date.today()
        trips = (
            TripInstance.objects.filter(date=today)
            .select_related("schedule__route", "schedule__bus", "schedule__driver")
            .order_by("schedule__departure_time")
        )

        self.stdout.write(f"Trip instances for {today}:")
        self.stdout.write("-" * 80)

        if not trips:
            self.stdout.write("No trip instances found for today.")
            return

        for trip in trips:
            status_color = {
                "pending": self.style.WARNING,
                "in_progress": self.style.HTTP_INFO,
                "completed": self.style.SUCCESS,
                "cancelled": self.style.ERROR,
            }.get(trip.status, self.style.NOTICE)

            self.stdout.write(
                f"ID: {trip.id:3d} | "
                f"{trip.schedule.route.route_name:20s} | "
                f"{trip.schedule.bus.bus_tag:10s} | "
                f"{trip.schedule.driver.name:20s} | "
                f'{trip.schedule.departure_time.strftime("%H:%M")} | '
                f"{status_color(trip.status.upper())}"
            )

    def start_trip(self, trip_id):
        try:
            trip = TripInstance.objects.select_related(
                "schedule__route", "schedule__bus", "schedule__driver"
            ).get(id=trip_id)

            self.stdout.write(f"Starting trip: {trip}")
            trip.start_trip()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Trip {trip_id} started successfully!")
            )

        except TripInstance.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Trip with ID {trip_id} not found"))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Cannot start trip: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error starting trip: {e}"))

    def complete_trip(self, trip_id):
        try:
            trip = TripInstance.objects.select_related(
                "schedule__route", "schedule__bus", "schedule__driver"
            ).get(id=trip_id)

            self.stdout.write(f"Completing trip: {trip}")
            trip.complete_trip()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Trip {trip_id} completed successfully!")
            )

        except TripInstance.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Trip with ID {trip_id} not found"))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Cannot complete trip: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error completing trip: {e}"))
