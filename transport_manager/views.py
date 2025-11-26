import json
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.views import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from authentication.models import DriverAuth
from transit_hub.forms import BusForm, DriverForm, HelperForm
from transit_hub.models import (
    Bus,
    Driver,
    Helper,
    Notice,
    Route,
    Stoppage,
    RouteStoppage,
)
from transport_manager.models import (
    LocationData,
    Transportation_schedules,
    TripInstance,
)
from transport_manager.serializers import (
    TodayTripsSerializer,
    DriverTripSerializer,
)
from transport_manager.sms import (
    send_sms,
    send_helper_sms,
    send_schedule_change_sms,
    send_schedule_cancellation_sms,
    send_helper_change_sms,
    send_helper_cancellation_sms,
)
from datetime import datetime, date
from django.core.paginator import Paginator


# Create your views here.
def subscription(request):
    return render(request, "transport_manager/subscription.html")


@login_required(login_url="diu_admin")
def dashboard(request):
    return render(request, "transport_manager/dashboard.html")


@login_required(login_url="diu_admin")
def today_schedules(request):


    current_time = datetime.now().replace(second=0, microsecond=0)
    current_day = localtime().strftime("%A").lower()
    today = date.today()

    # Get all active schedules for today
    schedules = (
        Transportation_schedules.objects.select_related(
            "bus", "driver", "route", "helper"
        )
        .filter(
            departure_time__gte=current_time.time(),
            days__contains=current_day,
            schedule_status=True,
        )
        .order_by("departure_time")
    )

    # Create or get trip instances for today's schedules and add to schedules
    for schedule in schedules:
        trip_instance, created = TripInstance.objects.get_or_create(
            schedule=schedule, date=today, defaults={"status": "pending"}
        )
        # Add trip instance to schedule object for easy access in template
        schedule.today_trip = trip_instance

    # Get all data for dropdowns
    routes = Route.objects.filter(route_status=True).order_by("route_name")
    buses = Bus.objects.filter(bus_status=True).order_by("bus_tag")
    drivers = Driver.objects.filter(driver_status=True).order_by("name")
    helpers = Helper.objects.filter(helper_status=True).order_by("name")

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
        selected_times = request.POST.getlist(
            "times"
        )  # Changed to getlist for multiple selections
        driver_id = request.POST.get("driver")
        helper_id = request.POST.get("helper")
        trip_type = request.POST.get("trip_type", "one_time")

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
                    # Create the schedule
                    new_schedule = Transportation_schedules.objects.create(
                        route=route_instance,
                        bus=bus_instance,
                        driver=driver_instance,
                        helper=helper_instance,
                        trip_type=trip_type,
                        departure_time=datetime.strptime(
                            selected_time, "%I:%M %p"
                        ).time(),
                        from_dsc=(direction == "from_dsc"),
                        to_dsc=(direction == "to_dsc"),
                        schedule_status=True,
                        days=localtime().strftime("%A").lower(),
                    )
                    driver_instance.total_trip_assigned += 1
                    bus_instance.route_assigned = True
                    bus_instance.save(update_fields=["route_assigned"])
                    driver_instance.save(update_fields=["total_trip_assigned"])
                    created_schedules += 1

                    # Create trip instance for today if the schedule should run today
                    today = datetime.now().date()
                    current_day = localtime().strftime("%A").lower()

                    # Check if this schedule should run today and if it's a future departure
                    current_time = localtime().time()
                    schedule_departure_time = datetime.strptime(
                        selected_time, "%I:%M %p"
                    ).time()

                    if (
                        current_day in new_schedule.days
                        and schedule_departure_time >= current_time
                    ):
                        try:
                            # Create trip instance for today
                            TripInstance.objects.get_or_create(
                                schedule=new_schedule,
                                date=today,
                                defaults={"status": "pending"},
                            )
                        except Exception as e:
                            print(f"Error creating trip instance: {e}")

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
    available_drivers = Driver.objects.filter(total_trip_assigned__lt=3)

    context = {
        "buses": Bus.objects.filter(route_assigned=False),
        "drivers": available_drivers,
        "helpers": Helper.objects.filter(bus_assigned=False),
        "times": ["11:15 AM", "1:20 PM", "4:20 PM", "6:10 PM"],
        "from_dsc_routes": from_dsc_routes,
        "to_dsc_routes": to_dsc_routes,
    }
    return render(request, "transport_manager/assign_schedule.html", context)


@login_required(login_url="diu_admin")
def manage_drivers_buses(request):
    drivers_list = Driver.objects.all()
    buses_list = Bus.objects.all()
    helpers_list = Helper.objects.all()

    driver_paginator = Paginator(drivers_list, 10)
    bus_paginator = Paginator(buses_list, 10)
    helper_paginator = Paginator(helpers_list, 10)

    driver_page_number = request.GET.get("driver_page")
    bus_page_number = request.GET.get("bus_page")
    helper_page_number = request.GET.get("helper_page")

    drivers = driver_paginator.get_page(driver_page_number)
    buses = bus_paginator.get_page(bus_page_number)
    helpers = helper_paginator.get_page(helper_page_number)

    # --- Form Handling ---
    driver_form = DriverForm()
    bus_form = BusForm()
    helper_form = HelperForm()

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
        elif "add_helper" in request.POST:
            helper_form = HelperForm(request.POST, request.FILES)
            if helper_form.is_valid():
                helper_form.save()
                messages.success(request, "Helper added successfully!")
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
        elif "edit_helper" in request.POST:
            helper_id = request.POST.get("helper_id")
            try:
                helper_instance = Helper.objects.get(id=helper_id)
                helper_form = HelperForm(
                    request.POST, request.FILES, instance=helper_instance
                )
                if helper_form.is_valid():
                    helper_form.save()
                    messages.success(request, "Helper updated successfully!")
                    return redirect("manage_drivers_buses")
            except Helper.DoesNotExist:
                messages.error(request, "Helper not found!")

    context = {
        "drivers": drivers,
        "buses": buses,
        "helpers": helpers,
        "driver_form": driver_form,
        "bus_form": bus_form,
        "helper_form": helper_form,
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
            from datetime import date

            schedule_id = request.POST.get("schedule_id")
            schedule = Transportation_schedules.objects.get(schedule_id=schedule_id)
            create_new_trip = request.POST.get("create_new_trip") == "on"

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
            print(
                f"Received edit for schedule {schedule_id}: route={route_id}, bus={bus_id}, driver={driver_id}, helper={helper_id}, departure_time={departure_time}, status={schedule_status}, from_dsc={from_dsc}"
            )
            # Parse new departure time
            new_departure_time = datetime.strptime(departure_time, "%H:%M").time()

            # Check if time has changed and create_new_trip is checked
            if create_new_trip and old_departure_time != new_departure_time:
                # Create a new schedule with the new time
                print("Creating new trip instance due to time change and 'create_new_trip' checked")
                route = Route.objects.get(id=route_id) if route_id else schedule.route
                bus = Bus.objects.get(id=bus_id) if bus_id else schedule.bus
                driver = (
                    Driver.objects.get(id=driver_id) if driver_id else schedule.driver
                )
                helper = Helper.objects.get(id=helper_id) if helper_id else None

                new_schedule = Transportation_schedules.objects.create(
                    route=route,
                    bus=bus,
                    driver=driver,
                    helper=helper,
                    trip_type=schedule.trip_type,
                    departure_time=new_departure_time,
                    from_dsc=from_dsc,
                    to_dsc=not from_dsc,
                    schedule_status=schedule_status,
                    audience=schedule.audience,
                    days=schedule.days,
                )

                # Create trip instance for new schedule
                TripInstance.objects.create(
                    schedule=new_schedule, date=date.today(), status="pending"
                )

                # Send SMS for new trip
                send_sms(driver, route, new_departure_time.strftime("%I:%M %p"), bus)
                if helper:
                    send_helper_sms(
                        helper, route, new_departure_time.strftime("%I:%M %p"), bus
                    )

                messages.success(
                    request,
                    "New trip created successfully! Original trip remains unchanged.",
                )
                return redirect("today_schedules")

            # Update the existing schedule (normal edit mode)
            # Update schedule fields
            if route_id:
                schedule.route = Route.objects.get(id=route_id)
                print(f"Updated route to {schedule.route}")
            if bus_id:
                print(f"Updated bus to {bus_id}")
                schedule.bus = Bus.objects.get(id=bus_id)
                print(f"Updated bus to {schedule.bus}")
            if driver_id:
                new_driver = Driver.objects.get(id=driver_id)
                # Only update driver stats if driver actually changed
                if schedule.driver != new_driver:
                    if schedule.driver:
                        schedule.driver.total_trip_assigned = max(
                            0, schedule.driver.total_trip_assigned - 1
                        )
                        schedule.driver.save()
                    new_driver.total_trip_assigned += 1
                    new_driver.save()
                    schedule.driver = new_driver

            if helper_id:
                try:
                    schedule.helper = Helper.objects.get(id=helper_id)
                except Helper.DoesNotExist:
                    schedule.helper = None
            else:
                schedule.helper = None

            if departure_time:
                schedule.departure_time = new_departure_time
                # Recalculate estimated end time
                from datetime import datetime as dt_class, date, timedelta

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
                    f"বাস পরিবর্তন: {old_bus.bus_name} থেকে {schedule.bus.bus_name}"
                )
            if old_departure_time != schedule.departure_time:
                changes.append(
                    f"সময় পরিবর্তন: {old_departure_time.strftime('%I:%M %p')} থেকে {schedule.departure_time.strftime('%I:%M %p')}"
                )
            if old_status != schedule.schedule_status:
                status_text = "সক্রিয়" if schedule.schedule_status else "নিষ্ক্রিয়"
                changes.append(f"অবস্থা পরিবর্তন: {status_text}")

            # Update or create today's trip instance
            today = date.today()
            trip_instance, created = TripInstance.objects.get_or_create(
                schedule=schedule, date=today, defaults={"status": "pending"}
            )
            print(f"Trip instance for today: {trip_instance}, created: {created}")
            # If trip instance already exists and schedule was modified, update it
            if not created and changes:
                # Only reset trip if it's still pending (don't interrupt in-progress trips)
                if trip_instance.status == "pending":
                    # Reset trip instance to reflect schedule changes
                    trip_instance.actual_start_time = None
                    trip_instance.actual_end_time = None
                    trip_instance.save(
                        update_fields=["actual_start_time", "actual_end_time"]
                    )
                    print(
                        f"Trip instance {trip_instance.id} updated due to schedule changes"
                    )
                elif trip_instance.status == "in_progress":
                    # Log that trip is in progress and can't be modified
                    print(
                        f"Trip instance {trip_instance.id} is in progress - schedule changes will apply to future trips"
                    )
                elif trip_instance.status == "completed":
                    # Log that trip is completed
                    print(
                        f"Trip instance {trip_instance.id} is completed - schedule changes don't affect completed trips"
                    )

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

            from datetime import date

            today = date.today()

            # Store details for SMS notification before deletion
            driver = schedule.driver
            helper = schedule.helper
            route = schedule.route
            departure_time = schedule.departure_time
            bus = schedule.bus

            # Update driver stats
            if driver:
                driver.total_trip_assigned = max(0, driver.total_trip_assigned - 1)
                driver.save()

            # Delete associated trip instances for today
            TripInstance.objects.filter(schedule=schedule, date=today).delete()

            # Delete the schedule
            schedule.delete()

            # Send cancellation SMS to driver
            if driver:
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


@csrf_exempt
def send_location(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Validate required fields
    required_fields = ["lat", "lon", "bus_name", "auth_token", "driver_id"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return JsonResponse(
            {"error": f"Missing required fields: {', '.join(missing_fields)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    lat = data.get("lat")
    lon = data.get("lon")
    bus_name = data.get("bus_name")
    auth_token = data.get("auth_token")
    driver_id = data.get("driver_id")
    is_trip_ending = data.get(
        "is_trip_ending", False
    )  # New parameter to indicate trip end

    # Validate latitude and longitude
    try:
        lat = float(lat)
        lon = float(lon)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("Invalid coordinates")
    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "Invalid latitude or longitude"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Authenticate driver
    try:
        driver_auth = DriverAuth.objects.select_related("driver").get(
            auth_token=auth_token
        )
    except DriverAuth.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid authentication token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        bus = Bus.objects.get(bus_name=bus_name)
        driver = Driver.objects.get(id=driver_id)

        # Auto-manage trip lifecycle based on location updates
        today = date.today()
        current_time = timezone.now().time()
        response_data = {
            "status": "success",
            "message": "Location updated successfully",
        }

        # Find current pending or in-progress trip for this driver
        current_trip = TripInstance.objects.filter(
            schedule__driver=driver, date=today, status__in=["pending", "in_progress"]
        ).first()

        if current_trip:
            # If trip is pending and driver sends location, auto-start the trip
            if current_trip.status == "pending" and not is_trip_ending:
                try:
                    current_trip.start_trip()
                    response_data["trip_started"] = True
                    response_data["message"] = (
                        "Location updated and trip started automatically"
                    )
                    response_data["trip_info"] = {
                        "trip_id": current_trip.id,
                        "route_name": current_trip.schedule.route.route_name,
                        "departure_time": current_trip.schedule.departure_time.strftime(
                            "%H:%M"
                        ),
                        "status": current_trip.status,
                    }
                except ValueError as e:
                    response_data["warning"] = f"Could not start trip: {str(e)}"

            # If driver indicates trip is ending and trip is in progress, complete it
            elif current_trip.status == "in_progress" and is_trip_ending:
                try:
                    current_trip.complete_trip()
                    response_data["trip_completed"] = True
                    response_data["message"] = (
                        "Location updated and trip completed automatically"
                    )
                    response_data["trip_info"] = {
                        "trip_id": current_trip.id,
                        "route_name": current_trip.schedule.route.route_name,
                        "actual_duration": (
                            str(
                                current_trip.actual_end_time
                                - current_trip.actual_start_time
                            )
                            if current_trip.actual_start_time
                            else None
                        ),
                        "status": current_trip.status,
                    }
                except ValueError as e:
                    response_data["warning"] = f"Could not complete trip: {str(e)}"

        # Update or create location data regardless of trip status
        LocationData.objects.update_or_create(
            bus=bus,
            driver=driver,
            defaults={"latitude": lat, "longitude": lon, "timestamp": datetime.now()},
        )

        return JsonResponse(response_data, status=status.HTTP_200_OK)

    except Bus.DoesNotExist:
        return JsonResponse(
            {"error": "Bus not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Driver.DoesNotExist:
        return JsonResponse(
            {"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def trips(request, driver_id, auth_token):
    """Get today's trip instances for a specific driver"""

    # Validate driver_id
    try:
        driver_id = int(driver_id)
    except (ValueError, TypeError):
        return Response(
            {"error": "Invalid driver ID"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Authenticate driver
    if not auth_token:
        return Response(
            {"error": "Authentication token required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        driver_auth = DriverAuth.objects.select_related("driver").get(
            auth_token=auth_token
        )
    except DriverAuth.DoesNotExist:
        return Response(
            {"error": "Invalid authentication token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        today = date.today()
        current_time = localtime().time()

        # Get today's trip instances for this driver
        trips_queryset = (
            TripInstance.objects.select_related(
                "schedule__route", "schedule__bus", "schedule__driver"
            )
            .filter(
                schedule__driver_id=driver_id,
                date=today,
                schedule__departure_time__gte=current_time,  # Only future trips
                status__in=["pending", "in_progress"],  # Exclude completed/cancelled
            )
            .order_by("schedule__departure_time")
        )

        serializer = DriverTripSerializer(trips_queryset, many=True)

        return Response(
            {"trips": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def trip_complete(request):
    """Complete a trip instance"""

    trip_id = json.loads(request.body).get("trip_id")
    auth_token = json.loads(request.body).get("auth_token")
    print(f"Received trip completion request for trip_id: {trip_id}")
    # Validate required fields
    if not trip_id or not auth_token:
        return Response(
            {"error": "Missing required fields: trip_id and auth_token"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Authenticate driver
    try:
        driver_auth = DriverAuth.objects.select_related("driver").get(
            auth_token=auth_token
        )
    except DriverAuth.DoesNotExist:
        return Response(
            {"error": "Invalid authentication token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        # Try to get trip instance by ID first, then by schedule_id for legacy support
        try:
            trip = TripInstance.objects.select_related(
                "schedule__driver", "schedule__route", "schedule__bus"
            ).get(id=trip_id)
        except (TripInstance.DoesNotExist, ValueError):
            # Legacy support: try to find today's trip instance for this schedule
            trip = TripInstance.objects.select_related(
                "schedule__driver", "schedule__route", "schedule__bus"
            ).get(schedule_id=trip_id, date=date.today())

        # Verify the authenticated driver owns this trip

        if trip.schedule.driver.id != driver_auth.driver.id:
            return Response(
                {"error": "Unauthorized: You can only complete your own trips"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Auto-start trip if it's still pending before completing
        if trip.status == "pending":
            try:
                trip.start_trip()
                print("Trip auto-started before completion")
            except ValueError as e:
                print(f"Error auto-starting trip: {str(e)}")
                return Response(
                    {"error": f"Cannot start trip: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Complete the trip using the model method
        trip.complete_trip()
        return Response(
            {
                "status": "success",
                "message": "Trip completed successfully",
                "trip_info": {
                    "route_name": trip.schedule.route.route_name,
                    "bus_tag": trip.schedule.bus.bus_tag,
                    "departure_time": trip.schedule.departure_time.strftime("%H:%M"),
                    "actual_start_time": (
                        trip.actual_start_time.isoformat()
                        if trip.actual_start_time
                        else None
                    ),
                    "actual_end_time": (
                        trip.actual_end_time.isoformat()
                        if trip.actual_end_time
                        else None
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )

    except TripInstance.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        print(f"ValueError: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@login_required
def add_notice(request):
    """Add notice page for admin"""

    if request.method == "POST":
        title = request.POST.get("title")
        notice_type = request.POST.get("notice_type")
        message = request.POST.get("message")
        route_id = request.POST.get("route")
        expires_at = request.POST.get("expires_at")
        is_active = request.POST.get("is_active") == "on"

        try:
            # Get route if specified
            route = None
            if route_id:
                route = Route.objects.get(id=route_id)

            # Parse expiration date
            expires_at_parsed = None
            if expires_at:
                expires_at_parsed = datetime.fromisoformat(expires_at.replace("T", " "))
                expires_at_parsed = timezone.make_aware(expires_at_parsed)

            # Create notice
            notice = Notice.objects.create(
                title=title,
                message=message,
                notice_type=notice_type,
                route=route,
                expires_at=expires_at_parsed,
                is_active=is_active,
            )

            route_name = route.route_name if route else "Global"
            messages.success(
                request, f"Notice '{title}' created successfully for {route_name}!"
            )
            return redirect("add_notice")

        except Route.DoesNotExist:
            messages.error(request, "Selected route not found.")
        except Exception as e:
            messages.error(request, f"Error creating notice: {str(e)}")

    # Get all routes for dropdown
    routes = Route.objects.all().order_by("route_name")

    # Get recent notices
    recent_notices = Notice.objects.all().order_by("-created_at")[:5]

    context = {
        "routes": routes,
        "recent_notices": recent_notices,
    }

    return render(request, "transport_manager/add_notice.html", context)


@login_required
def view_notices(request):
    """View all notices page"""
    from transit_hub.models import Notice

    notices = Notice.objects.select_related("route").order_by("-created_at")

    # Get unique routes for filter
    unique_routes = (
        Notice.objects.select_related("route")
        .exclude(route__isnull=True)
        .values_list("route__route_name", flat=True)
        .distinct()
    )

    # Pagination
    paginator = Paginator(notices, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "notices": page_obj,
        "unique_routes": unique_routes,
    }

    return render(request, "transport_manager/view_notices.html", context)


@login_required
@csrf_exempt
def toggle_notice(request):
    """Toggle notice active status"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            notice_id = data.get("notice_id")
            new_status = data.get("is_active")

            from transit_hub.models import Notice

            notice = Notice.objects.get(id=notice_id)
            notice.is_active = new_status
            notice.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": f"Notice {'activated' if new_status else 'deactivated'} successfully",
                    "is_active": notice.is_active,
                }
            )

        except Notice.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "Notice not found"}, status=404
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse(
        {"success": False, "message": "Invalid request method"}, status=405
    )


def load_google_maps_script(request):
    """Securely load Google Maps script without exposing API key to frontend"""
    from django.conf import settings
    from django.http import HttpResponse

    api_key = settings.GOOGLE_MAPS_API_KEY
    if not api_key:
        # Return empty script if no API key configured
        return HttpResponse(
            "console.warn('Google Maps API key not configured - running in demo mode');",
            content_type="application/javascript",
        )

    # Create a script that loads Google Maps without exposing the key
    script_content = f"""
// Secure Google Maps loader - API key never exposed to frontend
(function() {{
    if (typeof google !== 'undefined' && window.googleMapsLoaded) {{
        return; // Already loaded
    }}
    
    const script = document.createElement('script');
    script.async = true;
    script.defer = true;
    script.src = 'https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=marker&callback=initGoogleMapsGlobal&loading=async';
    script.onerror = function() {{
        console.warn('Google Maps API failed to load - running in demo mode');
        window.googleMapsLoaded = false;
        window.googleMapsApiLoaded = false;
    }};
    
    document.head.appendChild(script);
}})();

// Global initialization function
window.initGoogleMapsGlobal = function() {{
    window.googleMapsLoaded = true;
    window.googleMapsApiLoaded = true;
    console.log('Google Maps API loaded successfully');
    
    // Trigger any pending map initializations
    if (window.initGoogleMapsTracking) {{
        window.initGoogleMapsTracking();
    }}
    if (window.initGoogleMaps) {{
        window.initGoogleMaps();
    }}
}};

window.gm_authFailure = function() {{
    console.warn('Google Maps API authentication failed');
    window.googleMapsLoaded = false;
    window.googleMapsApiLoaded = false;
}};
"""

    return HttpResponse(script_content, content_type="application/javascript")


@login_required(login_url="diu_admin")
def trip_reports(request):

    # Get filter parameters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    driver_filter = request.GET.get("driver")
    route_filter = request.GET.get("route")
    status_filter = request.GET.get("status")
    bus_filter = request.GET.get("bus")

    # Default to last 7 days if no dates provided
    today = date.today()
    if not start_date:
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = today.strftime("%Y-%m-%d")

    # Base queryset
    trips = (
        TripInstance.objects.select_related(
            "schedule__route", "schedule__bus", "schedule__driver", "schedule__helper"
        )
        .filter(date__range=[start_date, end_date])
        .order_by("-date", "schedule__departure_time")
    )

    # Apply filters
    if driver_filter:
        trips = trips.filter(schedule__driver__id=driver_filter)
    if route_filter:
        trips = trips.filter(schedule__route__id=route_filter)
    if status_filter:
        trips = trips.filter(status=status_filter)
    if bus_filter:
        trips = trips.filter(schedule__bus__id=bus_filter)

    # Get statistics
    total_trips = trips.count()
    completed_trips = trips.filter(status="completed").count()
    in_progress_trips = trips.filter(status="in_progress").count()
    pending_trips = trips.filter(status="pending").count()
    cancelled_trips = trips.filter(status="cancelled").count()

    completion_rate = (completed_trips / total_trips * 100) if total_trips > 0 else 0

    # Pagination
    paginator = Paginator(trips, 20)  # 20 trips per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get data for filter dropdowns
    drivers = Driver.objects.filter(driver_status=True).order_by("name")
    routes = Route.objects.filter(route_status=True).order_by("route_name")
    buses = Bus.objects.filter(bus_status=True).order_by("bus_tag")

    # Trip status choices
    status_choices = TripInstance.TRIP_STATUS_CHOICES

    context = {
        "trips": page_obj,
        "total_trips": total_trips,
        "completed_trips": completed_trips,
        "in_progress_trips": in_progress_trips,
        "pending_trips": pending_trips,
        "cancelled_trips": cancelled_trips,
        "completion_rate": round(completion_rate, 1),
        "start_date": start_date,
        "end_date": end_date,
        "drivers": drivers,
        "routes": routes,
        "buses": buses,
        "status_choices": status_choices,
        "current_filters": {
            "driver": driver_filter,
            "route": route_filter,
            "status": status_filter,
            "bus": bus_filter,
        },
    }

    return render(request, "transport_manager/trip_reports.html", context)


@api_view(["GET"])
def trips_today(request):
    """Get all trip instances for today with optional filtering"""

    today = date.today()
    driver_id = request.query_params.get("driver_id")
    status_filter = request.query_params.get("status")

    queryset = TripInstance.objects.select_related(
        "schedule__route", "schedule__bus", "schedule__driver"
    ).filter(date=today)

    if driver_id:
        queryset = queryset.filter(schedule__driver_id=driver_id)

    if status_filter:
        queryset = queryset.filter(status=status_filter)

    queryset = queryset.order_by("schedule__departure_time")

    serializer = TodayTripsSerializer(queryset, many=True)

    return Response(
        {
            "date": today.isoformat(),
            "trips": serializer.data,
            "count": len(serializer.data),
        },
        status=status.HTTP_200_OK,
    )
