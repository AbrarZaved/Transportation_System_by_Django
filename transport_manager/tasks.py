from celery import shared_task
from celery.app import routes
from django.utils import timezone
from transportation_system.settings import BASE_DIR
from .models import Transportation_schedules, Bus, Driver
import requests
import environ
import os
from transport_manager.views import time_format


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
