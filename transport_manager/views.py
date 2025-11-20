import json
import os
from datetime import datetime as dt_class, date, timedelta
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q,F
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from rest_framework.views import csrf_exempt
from transit_hub.forms import BusForm, DriverForm
from transit_hub.models import Bus, Driver, Helper, Route, Stoppage
from transit_hub.models import RouteStoppage
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
        Transportation_schedules.objects.select_related(
            "bus", "driver", "route", "helper"
        )
        .filter(departure_time__gte=current_time)
        .order_by("departure_time")
    )

    # Get all data for dropdowns
    routes = Route.objects.filter(route_status=True).order_by("route_name")
    buses = Bus.objects.filter(route_assigned=False).order_by("bus_tag")
    drivers = Driver.objects.filter(bus_assigned=False).order_by("name")
    helpers = Helper.objects.all().order_by("name")

    return render(
        request,
        "transport_manager/today_schedules.html",
        {
            "schedules": schedules,
            "routes": routes,
            "buses": buses,
            "drivers": drivers,
            "helpers": helpers,
        },
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


def send_helper_sms(helper_instance, route_instance, selected_time, bus_instance):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"হেলপার {helper_instance.name}, আপনার বাস ডিউটি নির্ধারিত হয়েছে। রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। সময়মতো উপস্থিত থাকার অনুরোধ রইল।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": helper_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()

        print("Helper SMS Status Code:", response.status_code)
        print("Helper SMS Response:", response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"Helper SMS HTTP error: {http_err}")

    except Exception as err:
        print(f"Helper SMS error: {err}")


def send_schedule_change_sms(
    driver_instance, route_instance, selected_time, bus_instance, changes
):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"ড্রাইভার {driver_instance.name}, আপনার বাস ডিউটি পরিবর্তন হয়েছে। {changes}। \n\n নতুন তথ্য - রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। সময়মতো উপস্থিত থাকার অনুরোধ রইল।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": driver_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Driver change SMS Status Code:", response.status_code)
        print("Driver change SMS Response:", response.text)
    except Exception as err:
        print(f"Driver change SMS error: {err}")


def send_schedule_cancellation_sms(
    driver_instance, route_instance, selected_time, bus_instance
):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"ড্রাইভার {driver_instance.name}, আপনার বাস ডিউটি বাতিল হয়েছে। রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। অনুগ্রহ করে অফিসে যোগাযোগ করুন।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": driver_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Driver cancellation SMS Status Code:", response.status_code)
        print("Driver cancellation SMS Response:", response.text)
    except Exception as err:
        print(f"Driver cancellation SMS error: {err}")


def send_helper_change_sms(
    helper_instance, route_instance, selected_time, bus_instance, changes
):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"হেলপার {helper_instance.name}, আপনার বাস ডিউটি পরিবর্তন হয়েছে। {changes}। \n\n নতুন তথ্য - রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। সময়মতো উপস্থিত থাকার অনুরোধ রইল।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": helper_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Helper change SMS Status Code:", response.status_code)
        print("Helper change SMS Response:", response.text)
    except Exception as err:
        print(f"Helper change SMS error: {err}")


def send_helper_cancellation_sms(
    helper_instance, route_instance, selected_time, bus_instance
):
    env = environ.Env()
    env_file = os.path.join(BASE_DIR, ".env")
    environ.Env.read_env(env_file)
    url = "http://bulksmsbd.net/api/smsapi"
    message = f"হেলপার {helper_instance.name}, আপনার বাস ডিউটি বাতিল হয়েছে। রুট: {route_instance}, সময়: {selected_time}, বাস: {bus_instance} ({bus_instance.bus_tag})। অনুগ্রহ করে অফিসে যোগাযোগ করুন।"
    payload = {
        "api_key": env("API_KEY"),
        "senderid": env("SENDER_ID"),
        "number": helper_instance.phone_number,
        "message": message,
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Helper cancellation SMS Status Code:", response.status_code)
        print("Helper cancellation SMS Response:", response.text)
    except Exception as err:
        print(f"Helper cancellation SMS error: {err}")


@login_required(login_url="diu_admin")
def assign_schedule(request):
    if request.method == "POST":
        direction = request.POST.get("direction")
        route_id = request.POST.get("route")
        selected_buses = request.POST.get("buses")
        selected_times = request.POST.getlist(
            "times"
        )  # Changed to getlist for multiple selections
        driver_id = request.POST.get("driver")
        helper_id = request.POST.get("helper")

        # Validate that no more than 3 times are selected
        if len(selected_times) > 3:
            messages.error(
                request, "A driver can be assigned to maximum 3 trips at once."
            )
            return redirect("assign_schedule")

        bus_instance = Bus.objects.filter(bus_tag=selected_buses).first()
        driver_instance = Driver.objects.filter(id=driver_id).first()
        helper_instance = (
            Helper.objects.filter(id=helper_id).first() if helper_id else None
        )
        route_instance = Route.objects.filter(id=route_id).first()

        print(f"Selected Route ID: {route_id}")
        print(f"Selected Buses: {bus_instance}")
        print(f"Selected Driver ID: {driver_id}")
        print(f"Selected Helper ID: {helper_id}")
        print(f"Selected Times: {selected_times}")

        if bus_instance and driver_instance and route_instance and selected_times:
            # Create multiple schedule entries for each selected time
            created_schedules = 0
            for selected_time in selected_times:
                # Check if this exact schedule already exists
                existing_schedule = Transportation_schedules.objects.filter(
                    route=route_instance,
                    bus=bus_instance,
                    driver=driver_instance,
                    departure_time=datetime.strptime(selected_time, "%I:%M %p").time(),
                    from_dsc=(direction == "from_dsc"),
                    to_dsc=(direction == "to_dsc"),
                ).first()

                if not existing_schedule:
                    Transportation_schedules.objects.create(
                        route=route_instance,
                        bus=bus_instance,
                        driver=driver_instance,
                        helper=helper_instance,
                        departure_time=datetime.strptime(
                            selected_time, "%I:%M %p"
                        ).time(),
                        from_dsc=(direction == "from_dsc"),
                        to_dsc=(direction == "to_dsc"),
                        schedule_status=True,
                    )
                    driver_instance.total_buses_assigned += 1
                    driver_instance.save()
                    created_schedules += 1

                    # Send SMS notifications
                    send_sms(
                        driver_instance, route_instance, selected_time, bus_instance
                    )
                    if helper_instance:
                        send_helper_sms(
                            helper_instance, route_instance, selected_time, bus_instance
                        )

            if created_schedules > 0:
                messages.success(
                    request, f"Successfully created {created_schedules} schedule(s)!"
                )
            else:
                messages.warning(request, "All selected schedules already exist.")
        else:
            messages.error(request, "Please ensure all required fields are selected.")
            return redirect("assign_schedule")

        return redirect("assign_schedule")

    # Separate routes by direction for client-side filtering
    from_dsc_routes = Route.objects.filter(from_dsc=True, route_status=True)
    to_dsc_routes = Route.objects.filter(to_dsc=True, route_status=True)

    # Get today's date for filtering current schedules
    today = datetime.now().date()

    # Filter drivers who have less than 3 trips assigned today
    available_drivers = []
    for driver in Driver.objects.filter(total_buses_assigned__lt=3):
        trip_count = Transportation_schedules.objects.filter(
            driver=driver, created_at__date=today
        ).count()

        if trip_count < 3:
            # Add trip count as an attribute for display
            driver.current_trips = trip_count
            available_drivers.append(driver)

    context = {
        "buses": Bus.objects.filter(route_assigned=False),
        "drivers": available_drivers,
        "helpers": Helper.objects.filter(bus_assigned=False),
        "times": ["11:00 AM", "1:00 PM", "4:00 PM", "6:00 PM"],
        "from_dsc_routes": from_dsc_routes,
        "to_dsc_routes": to_dsc_routes,
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
                messages.success(request, "Driver added successfully!")
                return redirect("manage_drivers_buses")
        elif "add_bus" in request.POST:
            bus_form = BusForm(request.POST, request.FILES)
            if bus_form.is_valid():
                bus_form.save()
                messages.success(request, "Bus added successfully!")
                return redirect("manage_drivers_buses")
        elif "edit_driver" in request.POST:
            driver_id = request.POST.get("driver_id")
            try:
                driver_instance = Driver.objects.get(id=driver_id)
                driver_form = DriverForm(
                    request.POST, request.FILES, instance=driver_instance
                )
                if driver_form.is_valid():
                    driver_form.save()
                    messages.success(request, "Driver updated successfully!")
                    return redirect("manage_drivers_buses")
            except Driver.DoesNotExist:
                messages.error(request, "Driver not found!")
        elif "edit_bus" in request.POST:
            bus_id = request.POST.get("bus_id")
            try:
                bus_instance = Bus.objects.get(id=bus_id)
                bus_form = BusForm(request.POST, request.FILES, instance=bus_instance)
                if bus_form.is_valid():
                    bus_form.save()
                    messages.success(request, "Bus updated successfully!")
                    return redirect("manage_drivers_buses")
            except Bus.DoesNotExist:
                messages.error(request, "Bus not found!")

    context = {
        "drivers": drivers,
        "buses": buses,
        "driver_form": driver_form,
        "bus_form": bus_form,
    }
    return render(request, "transport_manager/manage_drivers_buses.html", context)


def route_management(request):
    routes_list = Route.objects.all()
    stoppages = Stoppage.objects.all()

    # Search functionality
    search_query = request.GET.get("search", "")
    print(f"Search query received: '{search_query}'")  # Debug print
    print(f"GET parameters: {request.GET}")  # Debug print

    if search_query:
        routes_list = routes_list.filter(
            Q(route_name__icontains=search_query)
            | Q(route_number__icontains=search_query)
        )
        print(f"Filtered routes count: {routes_list.count()}")  # Debug print

    # Pagination
    paginator = Paginator(routes_list, 15)  # 15 routes per page
    page_number = request.GET.get("page")
    routes = paginator.get_page(page_number)

    context = {
        "routes": routes,
        "stoppages": stoppages,
        "stoppages_json": json.dumps(list(stoppages.values("id", "stoppage_name"))),
        "search_query": search_query,
    }
    return render(request, "transport_manager/route_management.html", context)


@csrf_exempt
def route_stoppages(request):
    route_id = json.loads(request.body).get("route_id")
    stoppages = RouteStoppage.objects.filter(route_id=route_id)
    return JsonResponse(
        {"stoppages": list(stoppages.values("id", "stoppage__stoppage_name"))}
    )


def add_route(request):
    if request.method == "POST":
        route = Route(
            route_name=request.POST.get("route_name"),
            route_number=request.POST.get("route_number"),
            route_status=request.POST.get("route_status") == "on",
            from_dsc=bool(request.POST.get("from_dsc")),
            to_dsc=not bool(request.POST.get("from_dsc")),
        )
        route.save()

        stoppages = request.POST.getlist("stoppages[]")
        for stoppage_id in reversed(stoppages):
            stoppage = Stoppage.objects.get(id=stoppage_id)
            RouteStoppage.objects.create(route=route, stoppage=stoppage)
    messages.success(request, "Route added successfully")
    return redirect("route_management")


def update_route(request, id):
    route = Route.objects.get(id=id)
    if request.method == "POST":
        route.route_name = request.POST.get("route_name")
        route.route_number = request.POST.get("route_number")
        route.route_status = request.POST.get("route_status") == "on"
        route.from_dsc = bool(request.POST.get("from_dsc"))
        route.to_dsc = not bool(request.POST.get("from_dsc"))
        route.save()

        # Clear existing stoppages
        RouteStoppage.objects.filter(route=route).delete()

        stoppages = request.POST.getlist("stoppages[]")
        for stoppage_id in reversed(stoppages):
            stoppage = Stoppage.objects.get(id=stoppage_id)
            RouteStoppage.objects.create(route=route, stoppage=stoppage)
    messages.success(request, "Route updated successfully")
    return redirect("route_management")


@login_required(login_url="diu_admin")
def edit_schedule(request):
    if request.method == "POST":
        try:
            schedule_id = request.POST.get("schedule_id")
            schedule = Transportation_schedules.objects.get(schedule_id=schedule_id)

            # Store old values for comparison
            old_route = schedule.route
            old_bus = schedule.bus
            old_driver = schedule.driver
            old_helper = schedule.helper
            old_departure_time = schedule.departure_time
            old_status = schedule.schedule_status

            # Get new values from form
            route_id = request.POST.get("route")
            bus_id = request.POST.get("bus")
            driver_id = request.POST.get("driver")
            helper_id = request.POST.get("helper")
            departure_time = request.POST.get("departure_time")
            schedule_status = request.POST.get("schedule_status") == "true"
            from_dsc = request.POST.get("direction") == "from_dsc"

            # Update schedule fields
            if route_id:
                schedule.route = Route.objects.get(id=route_id)
            if bus_id:
                schedule.bus = Bus.objects.get(id=bus_id)
            if driver_id:
                schedule.driver = Driver.objects.get(id=driver_id)
                schedule.driver.total_buses_assigned += 1
            if helper_id:
                try:
                    schedule.helper = Helper.objects.get(id=helper_id)
                except Helper.DoesNotExist:
                    schedule.helper = None
            else:
                schedule.helper = None

            if departure_time:
                schedule.departure_time = datetime.strptime(
                    departure_time, "%H:%M"
                ).time()
                # Recalculate estimated end time


                dt = dt_class.combine(date.today(), schedule.departure_time)
                dt += timedelta(hours=3)
                schedule.estimated_end_time = dt.time()

            schedule.schedule_status = schedule_status
            schedule.from_dsc = from_dsc
            schedule.to_dsc = not from_dsc

            # Check what changed and send notifications
            changes = []
            if old_route != schedule.route:
                changes.append(
                    f"রুট পরিবর্তন: {old_route.route_name} থেকে {schedule.route.route_name}"
                )
            if old_bus != schedule.bus:
                changes.append(
                    f"বাস পরিবর্তন: {old_bus.bus_tag} থেকে {schedule.bus.bus_tag}"
                )
            if old_departure_time != schedule.departure_time:
                changes.append(
                    f"সময় পরিবর্তন: {old_departure_time.strftime('%I:%M %p')} থেকে {schedule.departure_time.strftime('%I:%M %p')}"
                )
            if old_status != schedule.schedule_status:
                status_text = "সক্রিয়" if schedule.schedule_status else "নিষ্ক্রিয়"
                changes.append(f"অবস্থা পরিবর্তন: {status_text}")

            schedule.save()

            # Send SMS notifications if there are changes
            if changes and schedule.schedule_status:
                try:
                    # Notify driver about changes
                    if old_driver == schedule.driver:
                        # Same driver, notify about changes
                        change_text = ", ".join(changes)
                        send_schedule_change_sms(
                            schedule.driver,
                            schedule.route,
                            schedule.departure_time.strftime("%I:%M %p"),
                            schedule.bus,
                            change_text,
                        )
                    else:
                        # Driver changed, notify both old and new
                        if old_driver:
                            send_schedule_cancellation_sms(
                                old_driver, old_route, old_departure_time, old_bus
                            )
                        send_sms(
                            schedule.driver,
                            schedule.route,
                            schedule.departure_time.strftime("%I:%M %p"),
                            schedule.bus,
                        )

                    # Notify helper if assigned
                    if schedule.helper:
                        if old_helper != schedule.helper:
                            # Helper changed or newly assigned
                            send_helper_sms(
                                schedule.helper,
                                schedule.route,
                                schedule.departure_time.strftime("%I:%M %p"),
                                schedule.bus,
                                schedule.driver,
                            )
                        elif changes:
                            # Same helper, notify about changes
                            change_text = ", ".join(changes)
                            send_helper_change_sms(
                                schedule.helper,
                                schedule.route,
                                schedule.departure_time.strftime("%I:%M %p"),
                                schedule.bus,
                                change_text,
                            )

                    # If helper was removed
                    elif old_helper and not schedule.helper:
                        send_helper_cancellation_sms(
                            old_helper, old_route, old_departure_time, old_bus
                        )

                except Exception as sms_error:
                    print(f"SMS notification failed: {sms_error}")

            if changes:
                messages.success(
                    request,
                    f"Schedule updated successfully! Changes: {', '.join(changes)}",
                )
            else:
                messages.success(request, "Schedule updated successfully!")

        except Transportation_schedules.DoesNotExist:
            messages.error(request, "Schedule not found!")
        except Exception as e:
            messages.error(request, f"Error updating schedule: {str(e)}")

    return redirect("today_schedules")


@login_required(login_url="diu_admin")
def delete_schedule(request):
    if request.method == "POST":
        schedule_id = request.POST.get("schedule_id")

        try:
            schedule = Transportation_schedules.objects.get(schedule_id=schedule_id)

            # Store details for SMS notification before deletion
            driver = schedule.driver
            helper = schedule.helper
            route = schedule.route
            departure_time = schedule.departure_time
            bus = schedule.bus
            driver.total_buses_assigned -= 1
            driver.save()
            # Delete the schedule
            schedule.delete()

            # Send cancellation SMS to driver
            send_schedule_cancellation_sms(driver, route, departure_time, bus)

            # Send cancellation SMS to helper if assigned
            if helper:
                send_helper_cancellation_sms(helper, route, departure_time, bus)

            messages.success(
                request, "Schedule deleted successfully and notifications sent!"
            )

        except Transportation_schedules.DoesNotExist:
            messages.error(request, "Schedule not found!")
        except Exception as e:
            messages.error(request, f"Error deleting schedule: {str(e)}")

    return redirect("today_schedules")
