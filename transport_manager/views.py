import json
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime
from redis import auth
from rest_framework import status
from rest_framework.views import csrf_exempt
from authentication.models import DriverAuth
from transit_hub.forms import BusForm, DriverForm
from transit_hub.models import Bus, Driver, Helper, Route, Stoppage, RouteStoppage
from transport_manager.models import LocationData, Transportation_schedules
from transport_manager.sms import (
    send_sms,
    send_helper_sms,
    send_schedule_change_sms,
    send_schedule_cancellation_sms,
    send_helper_change_sms,
    send_helper_cancellation_sms,
)
from datetime import datetime
from django.db import transaction
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
    schedules = (
        Transportation_schedules.objects.select_related(
            "bus", "driver", "route", "helper"
        )
        .filter(departure_time__gte=current_time, days__contains=current_day)
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
                    Transportation_schedules.objects.create(
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
    available_drivers = Driver.objects.filter(total_trip_assigned__lt=3)

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

            # Parse new departure time
            new_departure_time = datetime.strptime(departure_time, "%H:%M").time()

            # Check if time has changed and create_new_trip is checked
            if create_new_trip and old_departure_time != new_departure_time:
                # Create a new schedule with the new time
                route = Route.objects.get(id=route_id) if route_id else schedule.route
                bus = Bus.objects.get(id=bus_id) if bus_id else schedule.bus
                driver = (
                    Driver.objects.get(id=driver_id) if driver_id else schedule.driver
                )
                helper = Helper.objects.get(id=helper_id) if helper_id else None

                Transportation_schedules.objects.create(
                    route=route,
                    bus=bus,
                    driver=driver,
                    helper=helper,
                    trip_type=schedule.trip_type,
                    departure_time=new_departure_time,
                    from_dsc=from_dsc,
                    to_dsc=not from_dsc,
                    schedule_status=schedule_status,
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
            if bus_id:
                schedule.bus = Bus.objects.get(id=bus_id)
            if driver_id:
                schedule.driver = Driver.objects.get(id=driver_id)
                schedule.driver.total_trip_assigned += 1
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
            driver.total_trip_assigned -= 1
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
    
    # Validate latitude and longitude
    try:
        lat = float(lat)
        lon = float(lon)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("Invalid coordinates")
    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "Invalid latitude or longitude"}, status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate driver
    try:
        driver_auth = DriverAuth.objects.select_related('driver').get(auth_token=auth_token)
    except DriverAuth.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid authentication token"}, status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        bus = Bus.objects.get(bus_name=bus_name)
        driver = Driver.objects.get(id=driver_id)
        
        # Update or create location data
        LocationData.objects.update_or_create(
            bus=bus,
            driver=driver,
            defaults={"latitude": lat, "longitude": lon, "timestamp": datetime.now()},
        )
        
        return JsonResponse(
            {"status": "success", "message": "Location updated successfully"},
            status=status.HTTP_200_OK
        )
        
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
            {"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def trips(request, driver_id, auth_token):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    # Validate driver_id
    try:
        driver_id = int(driver_id)
    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "Invalid driver ID"}, status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate driver
    if not auth_token:
        return JsonResponse(
            {"error": "Authentication token required"}, status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        driver_auth = DriverAuth.objects.select_related('driver').get(auth_token=auth_token)
    except DriverAuth.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid authentication token"}, status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        current_day = localtime().strftime("%A").lower()
        current_time = localtime().time()
        
        # Optimized query with select_related to reduce database hits
        trips_queryset = Transportation_schedules.objects.select_related(
            'route', 'bus', 'driver'
        ).filter(
            driver_id=driver_id,
            days__contains=current_day,
            schedule_status=True,
            departure_time__gte=current_time  # Only future trips
        ).order_by('departure_time')
        
        trips_data = []
        for trip in trips_queryset:
            trips_data.append({
                "schedule_id": trip.schedule_id,
                "route_name": trip.route.route_name,
                "bus_name": trip.bus.bus_name,
                "bus_tag": trip.bus.bus_tag,
                "driver_name": trip.driver.name,
                "departure_time": trip.departure_time.strftime("%H:%M"),
                "from_dsc": trip.from_dsc,
                "to_dsc": trip.to_dsc
            })
        
        return JsonResponse(
            {"trips": trips_data, "count": len(trips_data)}, 
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
def trip_complete(request):
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
    
    schedule_id = data.get("schedule_id")
    auth_token = data.get("auth_token")
    
    # Validate required fields
    if not schedule_id or not auth_token:
        return JsonResponse(
            {"error": "Missing required fields: schedule_id and auth_token"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    # Authenticate driver
    try:
        driver_auth = DriverAuth.objects.select_related('user').get(auth_token=auth_token)
    except DriverAuth.DoesNotExist:
        return JsonResponse(
            {"error": "Invalid authentication token"}, status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Use select_related to optimize the query
        schedule = Transportation_schedules.objects.select_related(
            'driver', 'route', 'bus'
        ).get(schedule_id=schedule_id)
        
        # Verify the authenticated driver owns this trip
        if schedule.driver.id != driver_auth.user.id:
            return JsonResponse(
                {"error": "Unauthorized: You can only complete your own trips"},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Check if trip is already completed
        if not schedule.schedule_status:
            return JsonResponse(
                {"error": "Trip already completed"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use atomic operation to ensure data consistency

        with transaction.atomic():
            driver = schedule.driver
            driver.total_trip_completed = F("total_trip_completed") + 1
            driver.total_trip_assigned = F("total_trip_assigned") - 1
            driver.save(update_fields=['total_trip_completed', 'total_trip_assigned'])
            
            # Mark schedule as completed
            schedule.schedule_status = False
            schedule.save(update_fields=['schedule_status'])
        
        return JsonResponse(
            {
                "status": "success",
                "message": "Trip completed successfully",
                "trip_info": {
                    "route_name": schedule.route.route_name,
                    "bus_tag": schedule.bus.bus_tag,
                    "departure_time": schedule.departure_time.strftime("%H:%M")
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Transportation_schedules.DoesNotExist:
        return JsonResponse(
            {"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
