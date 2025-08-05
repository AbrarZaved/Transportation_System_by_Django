import json
import os
import sys
import time
from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from transit_hub.forms import BusForm, DriverForm
from transit_hub.models import Bus, Driver, Route
from transport_manager.models import Transportation_schedules
import environ
from datetime import datetime
from transportation_system.settings import BASE_DIR
from django.core.paginator import Paginator


def send_sms(driver_instance, route_instance, selected_time, bus_instance):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"ড্রাইভার {driver_instance.name}, আপনার বাস ডিউটি নির্ধারিত হয়েছে। রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। সময়মতো উপস্থিত থাকার অনুরোধ রইল।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": driver_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()  # raises exception for HTTP errors

        print("Status Code:", response.status_code)
        print("Response:", response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")

    except Exception as err:
        print(f"An error occurred: {err}")


def time_format(time_str):
    try:
        time_obj = datetime.strptime(time_str.strip(), "%I:%M %p").time()
        return time_obj.strftime("%H:%M:%S.%f")
    except ValueError:
        return None


# Create your views here.
def subscription(request):
    return render(request, "transport_manager/subscription.html")


def admin_login(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")
        user = authenticate(request, employee_id=employee_id, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid Employee ID or Password.")
            return redirect("diu_admin")
    return render(request, "transport_manager/admin_login.html")


@login_required(login_url="diu_admin")
def dashboard(request):
    return render(request, "transport_manager/dashboard.html")


@login_required(login_url="diu_admin")
def today_schedules(request):
    current_time = datetime.now().replace(second=0, microsecond=0)
    schedules = (
        Transportation_schedules.objects.select_related("bus", "driver", "route")
        .filter(departure_time__gte=current_time)
        .order_by("departure_time")
    )
    return render(
        request, "transport_manager/today_schedules.html", {"schedules": schedules}
    )


def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("diu_admin")


def filter_route(request):
    if request.method == "POST":
        data = json.loads(request.body)
        selected_route = data.get("direction")
        print(f"Selected Route: {selected_route}")
        if selected_route:
            routes = Route.objects.filter(
                from_dsc=True if selected_route == "from_dsc" else False
            )
            return JsonResponse(
                {
                    "status": "success",
                    "routes": [
                        {
                            "id": route.id,
                            "name": route.route_name,
                        }
                        for route in routes
                    ],
                }
            )


@login_required(login_url="diu_admin")
def assign_schedule(request):
    if request.method == "POST":
        direction = request.POST.get("direction")
        route_id = request.POST.get("route")
        selected_buses = request.POST.get("buses")
        selected_time = request.POST.get("time")
        driver_id = request.POST.get("driver")

        bus_instance = Bus.objects.filter(bus_tag=selected_buses).first()
        driver_instance = Driver.objects.filter(id=driver_id).first()
        route_instance = Route.objects.filter(id=route_id).first()
        print(f"Selected Route ID: {route_id}")
        print(f"Selected Buses: {bus_instance}")
        print(f"Selected Driver ID: {driver_id}")
        if bus_instance and driver_instance:
            Transportation_schedules.objects.create(
                route_id=route_id,
                bus=bus_instance,
                driver=driver_instance,
                departure_time=datetime.strptime(selected_time, "%I:%M %p").time(),
                from_dsc=(direction == "from_dsc"),
                to_dsc=(direction == "to_dsc"),
                schedule_status=True,
            )
            messages.success(request, "Schedule assigned successfully!")
        else:
            messages.error(request, "No valid bus or driver selected.")
            return redirect("assign_schedule")

        send_sms(driver_instance, route_instance, selected_time, bus_instance)
        return redirect("assign_schedule")

    context = {
        "buses": Bus.objects.filter(route_assigned=False),
        "drivers": Driver.objects.filter(bus_assigned=False),
        "times": ["11:00 AM", "1:00 PM", "4:00 PM", "6:00 PM"],
    }
    return render(request, "transport_manager/assign_schedule.html", context)


@login_required(login_url="diu_admin")
def manage_drivers_buses(request):
    drivers_list = Driver.objects.all()
    buses_list = Bus.objects.all()

    driver_paginator = Paginator(drivers_list, 10)
    bus_paginator = Paginator(buses_list, 10)

    driver_page_number = request.GET.get("driver_page")
    bus_page_number = request.GET.get("bus_page")

    drivers = driver_paginator.get_page(driver_page_number)
    buses = bus_paginator.get_page(bus_page_number)

    # --- Form Handling ---
    driver_form = DriverForm()
    bus_form = BusForm()

    if request.method == "POST":
        if "add_driver" in request.POST:
            driver_form = DriverForm(request.POST, request.FILES)
            if driver_form.is_valid():
                driver_form.save()
                return redirect("manage_drivers_buses")
        elif "add_bus" in request.POST:  # Check for the 'add_bus' button name
            bus_form = BusForm(request.POST, request.FILES)
            if bus_form.is_valid():
                bus_form.save()
                return redirect("manage_drivers_buses")  # Redirect to refresh the list

    context = {
        "drivers": drivers,
        "buses": buses,
        "driver_form": driver_form,
        "bus_form": bus_form,  # Pass the bus form to the template
    }
    return render(request, "transport_manager/manage_drivers_buses.html", context)
