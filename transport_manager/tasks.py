from celery import shared_task
from celery.app import routes
from django.utils import timezone
from transportation_system.settings import BASE_DIR
from .models import Transportation_schedules, TripInstance
from transit_hub.models import Bus, Driver
import requests
import environ
import os
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def time_format(time_obj):
    """Format time object to string"""
    if time_obj:
        return time_obj.strftime("%H:%M")
    return ""


def send_sms_task(routes):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    for route in routes:
        message = f"ড্রাইভার {route.driver.name}, আপনার বাস ডিউটি নির্ধারিত হয়েছে। রুট: {route.route}, সময়: {time_format(route.departure_time)}, বাস: {route.bus} ({route.bus.bus_tag})। সময়মতো উপস্থিত থাকার অনুরোধ রইল।"
        payload = {
            "api_key": env("API_KEY"),
            "senderid": env("SENDER_ID"),
            "number": route.driver.phone_number,
            "message": message,
        }

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            print("Status Code:", response.status_code)
            print("Response:", response.text)

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")


@shared_task
def auto_sms_task():
    routes = Transportation_schedules.objects.filter(
        schedule_status=True, bus__bus_tag__icontains="R"
    )
    if routes.exists():
        send_sms_task(routes)
        return f"SMS sent to {routes.count()} drivers."
    else:
        return "No active routes found for SMS sending."


@shared_task
def cleanup_old_schedules():
    """Legacy function - now replaced by trip instance cleanup"""
    now = timezone.now()
    expired_schedules = Transportation_schedules.objects.filter(
        estimated_end_time__lt=now, schedule_status=True
    )
    for schedule in expired_schedules:
        schedule.schedule_status = False
        schedule.save()
        schedule.driver.bus_assigned = False
        schedule.driver.save()
        schedule.bus.route_assigned = False
        schedule.bus.save()
    return f"Cleaned up {expired_schedules.count()} expired schedules."


# ============ NEW TRIP INSTANCE TASKS ============


@shared_task
def generate_daily_trip_instances():
    """
    Generate trip instances for all active schedules that should run today.
    This task should be run daily at midnight.
    """
    today = date.today()
    current_day = timezone.localtime().strftime("%A").lower()

    logger.info(f"Generating trip instances for {today} ({current_day})")

    # Get all active schedules that should run today
    active_schedules = Transportation_schedules.objects.filter(
        schedule_status=True, days__contains=current_day
    ).select_related("route", "bus", "driver")

    created_count = 0
    skipped_count = 0
    errors = []

    for schedule in active_schedules:
        try:
            # Check if trip instance already exists for today
            trip_instance, created = TripInstance.objects.get_or_create(
                schedule=schedule, date=today, defaults={"status": "pending"}
            )

            if created:
                created_count += 1
                logger.info(
                    f"Created trip instance for schedule {schedule.schedule_id} - {schedule.route.route_name}"
                )
            else:
                skipped_count += 1
                logger.debug(
                    f"Trip instance already exists for schedule {schedule.schedule_id}"
                )

        except Exception as e:
            error_msg = f"Error creating trip instance for schedule {schedule.schedule_id}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)

    logger.info(
        f"Trip instance generation completed. Created: {created_count}, Skipped: {skipped_count}, Errors: {len(errors)}"
    )

    return {
        "date": today.isoformat(),
        "created_count": created_count,
        "skipped_count": skipped_count,
        "errors": errors,
    }


@shared_task
def cleanup_old_trip_instances():
    """
    Clean up trip instances older than 30 days.
    This helps maintain database performance.
    """
    cutoff_date = date.today() - timedelta(days=30)

    logger.info(f"Cleaning up trip instances older than {cutoff_date}")

    # Delete trip instances older than 30 days
    deleted_count, _ = TripInstance.objects.filter(date__lt=cutoff_date).delete()

    logger.info(f"Cleaned up {deleted_count} old trip instances")

    return {"cutoff_date": cutoff_date.isoformat(), "deleted_count": deleted_count}


@shared_task
def auto_complete_overdue_trips():
    """
    Automatically mark trips as completed if they are significantly overdue.
    This prevents resources from being locked indefinitely.
    """
    now = timezone.now()

    # Find trips that are in_progress and overdue by more than 2 hours
    overdue_threshold = now - timedelta(hours=2)

    overdue_trips = TripInstance.objects.filter(
        status="in_progress", actual_start_time__lt=overdue_threshold
    ).select_related("schedule__bus", "schedule__driver")

    completed_count = 0
    errors = []

    for trip in overdue_trips:
        try:
            trip.complete_trip()
            completed_count += 1
            logger.warning(f"Auto-completed overdue trip: {trip}")
        except Exception as e:
            error_msg = f"Error auto-completing trip {trip.id}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)

    logger.info(f"Auto-completed {completed_count} overdue trips")

    return {"completed_count": completed_count, "errors": errors}


@shared_task
def reset_daily_assignments():
    """
    Reset bus and driver assignments at the end of each day.
    This ensures a clean slate for the next day.
    """
    logger.info("Resetting daily assignments")

    # Reset bus assignments
    bus_reset_count = Bus.objects.filter(route_assigned=True).update(
        route_assigned=False
    )

    # Reset driver trip assignments to 0 (they should be 0 if all trips are completed)
    driver_reset_count = Driver.objects.filter(total_trip_assigned__gt=0).update(
        total_trip_assigned=0
    )

    logger.info(
        f"Reset assignments - Buses: {bus_reset_count}, Drivers: {driver_reset_count}"
    )

    return {
        "bus_reset_count": bus_reset_count,
        "driver_reset_count": driver_reset_count,
    }
