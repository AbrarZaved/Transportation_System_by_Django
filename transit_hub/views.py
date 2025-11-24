from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from social_core.backends import username
from authentication.models import Preference, Student, StudentReview
from transit_hub.models import Route, Bus, Notice
from django.http import JsonResponse
import json
from transit_hub.serializer import RouteSerializer, RouteStoppageSerializer
from transport_manager.models import (
    Transportation_schedules,
    LocationData,
    TripInstance,
)
from .models import RouteStoppage as RouteStoppageModel
from django.db.models import F
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime
from django.db.models import Q
from .models import Stoppage
from django.conf import settings


# e.g., 08:30 AM


def index(request):
    user = request.session.get("username")
    preferences = []
    current_time = localtime().time()
    current_day = localtime().strftime("%A").lower()

    # Get upcoming buses data (all routes within next 1 hour)
    upcoming_buses_data = cache.get("upcoming_buses")
    if upcoming_buses_data is None:
        # Calculate time range (current time to 1 hour from now)
        current_datetime = localtime()
        one_hour_later = (current_datetime + timedelta(hours=1)).time()

        # Get all upcoming schedules for today within next hour
        all_schedules = (
            Transportation_schedules.objects.select_related("bus", "driver", "route")
            .filter(
                departure_time__gte=current_time,
                departure_time__lte=one_hour_later,
                days__contains=current_day,
            )
            .order_by("departure_time")
        )

        # Group by route and direction, get the next departure for each
        upcoming_buses_data = []
        processed_routes = set()
        for schedule in all_schedules:
            route_direction_key = f"{schedule.route.id}_{schedule.from_dsc}"

            if route_direction_key not in processed_routes:
                processed_routes.add(route_direction_key)

                upcoming_buses_data.append(
                    {
                        "route_name": schedule.route.route_name,
                        "direction": "From DSC" if schedule.from_dsc else "To DSC",
                        "departure_time": schedule.departure_time.strftime("%I:%M %p"),
                        "route_id": schedule.route.id,
                        "from_dsc": schedule.from_dsc,
                    }
                )
        cache.set(
            "upcoming_buses", upcoming_buses_data, timeout=60
        )  # 1 minute cache for hourly data

    # Get active and visible notices

    now = timezone.now()

    active_notices = (
        Notice.objects.filter(is_active=True, created_at__lte=now)
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
        .select_related("route")
    )

    # Organize notices by route
    notices_by_route = {}
    global_notices = []

    for notice in active_notices:
        if notice.route:
            route_id = notice.route.id
            if route_id not in notices_by_route:
                notices_by_route[route_id] = []
            notices_by_route[route_id].append(notice)
        else:
            global_notices.append(notice)

    if user:
        preferences = list(
            Preference.objects.filter(student__username=user).order_by("-created_at")[
                :3
            ]
        )

    # Get recent reviews for carousel (4+ star reviews)
    try:
        recent_reviews = (
            StudentReview.objects.select_related("student", "bus", "driver")
            .filter(is_approved=True, rating__gte=4)
            .order_by("-created_at")[:6]
        )

        reviews_data = []
        for review in recent_reviews:
            target_name = review.bus.bus_name if review.bus else review.driver.name
            target_type = "Bus" if review.bus else "Driver"

            reviews_data.append(
                {
                    "id": review.id,
                    "student_name": review.student.name,
                    "target_name": target_name,
                    "target_type": target_type,
                    "rating": review.rating,
                    "comment": (
                        review.comment[:100] + "..."
                        if len(review.comment) > 100
                        else review.comment
                    ),
                    "created_at": review.created_at.strftime("%B %d, %Y"),
                }
            )
    except Exception as e:
        # Fallback if StudentReview model doesn't exist or there's an error
        reviews_data = []
    return render(
        request,
        "transit_hub/index.html",
        {
            "preferences": preferences,
            "upcoming_buses": upcoming_buses_data,
            "notices_by_route": notices_by_route,
            "global_notices": global_notices,
            "recent_reviews": reviews_data,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        },
    )


@sync_to_async
def get_schedules(trip_type, place, username=None):
    from datetime import date

    today = date.today()
    current_time = localtime().time()
    current_day = localtime().strftime("%A").lower()
    # Search for trip instances that are available today
    trip_instances = (
        TripInstance.objects.select_related(
            "schedule__bus", "schedule__driver", "schedule__route"
        )
        .filter(
            # Filter by route name or stoppage name
            Q(schedule__route__route_name__icontains=place)
            | Q(
                schedule__route__routestoppage__stoppage__stoppage_name__icontains=place
            ),
            # Filter by direction
            schedule__from_dsc=(trip_type == "From DSC"),
            # Only today's trips
            date=today,
            # Only future departures
            schedule__departure_time__gte=current_time,
            # Only pending or in_progress trips (available trips)
            status__in=["pending", "in_progress"],
            # Ensure the schedule is active
            schedule__schedule_status=True,
        )
        .distinct()
        .order_by("schedule__departure_time")
    )

    route_ids = trip_instances.values_list("schedule__route__id", flat=True).distinct()
    route_details = RouteStoppageModel.objects.filter(route_id__in=route_ids)

    stoppages_by_route = {}
    for stop in route_details:
        stoppages_by_route.setdefault(stop.route_id, []).append(stop)

    data = []
    for trip_instance in trip_instances:
        schedule = trip_instance.schedule
        route_obj = schedule.route
        route_id = route_obj.id

        # Determine status display
        status_display = ""
        if trip_instance.status == "pending":
            status_display = "Available"
        elif trip_instance.status == "in_progress":
            status_display = "Departing Soon"

        data.append(
            {
                "trip_id": trip_instance.id,
                "route": RouteSerializer(route_obj).data,
                "route_name": route_obj.route_name,
                "audience": schedule.get_audience_display(),
                "departure_time": (
                    schedule.departure_time.strftime("%I:%M %p")
                    if username
                    else status_display
                ),
                "status": trip_instance.status,
                "status_display": status_display,
                "stoppage_names": [
                    stoppage.stoppage.stoppage_name
                    for stoppage in stoppages_by_route.get(route_id, [])
                ],
                "bus": {
                    "id": schedule.bus.id,
                    "name": schedule.bus.bus_name,
                    "capacity": schedule.bus.bus_capacity,
                    "bus_image": (
                        schedule.bus.bus_photo.url if schedule.bus.bus_photo else None
                    ),
                },
                "driver": {
                    "id": schedule.driver.id,
                    "name": schedule.driver.name,
                },
            }
        )

    return data


@sync_to_async(thread_sensitive=False)
def save_preference_by_session(username, place):
    student = Student.objects.filter(username=username).first()

    if (
        student
        and not Preference.objects.filter(
            student=student, searched_locations=place
        ).exists()
    ):
        Preference.objects.create(
            student=student,
            searched_locations=place,
            total_searches=1,
        )
    else:
        Preference.objects.filter(student=student, searched_locations=place).update(
            total_searches=F("total_searches") + 1
        )


@sync_to_async
def get_username_from_session(request):
    return request.session.get("username")


async def search_route(request):
    if request.method == "POST":
        body = json.loads(request.body)
        trip_type = body.get("tripType")
        place = body.get("place")
        if trip_type == "From DSC" and place == "Daffodil Smart City":
            return JsonResponse({"routes": []})

        # Get username from session using sync helper
        username = await get_username_from_session(request)
        data = await get_schedules(trip_type, place, username=username)

        try:
            if data and username:
                await save_preference_by_session(username, place)
        except Exception as e:
            print(e)
        return JsonResponse({"routes": data})

    return JsonResponse({"message": "Invalid request method"}, status=405)


class RouteStoppage(APIView):
    def get(self, request, id=None):
        if id:
            route_stoppage = Route.objects.get(id=id)
            serializer = RouteSerializer(route_stoppage)
            return Response(serializer.data)
        route_stoppage = Route.objects.all()
        serializer = RouteSerializer(route_stoppage, many=True)
        return Response(serializer.data)


class RouteDetails(APIView):
    def get(self, request, id=None):
        if id:
            route_id = self.kwargs["id"]
            try:
                route = Route.objects.get(id=route_id)
                route_details = RouteStoppageModel.objects.filter(route=route)
                stoppages = RouteStoppageSerializer(route_details, many=True).data
                return Response(
                    {
                        "route": RouteSerializer(route).data,  # Full data
                        "stoppage_names": [
                            stoppage["stoppage_name"] for stoppage in stoppages
                        ],
                    }
                )
            except Route.DoesNotExist:
                return Response({"error": "Route not found"})
        return Response(
            {"Routes": RouteSerializer(Route.objects.all(), many=True).data}
        )


def about_us(request):
    return render(
        request,
        "transit_hub/about.html",
        {"google_maps_api_key": settings.GOOGLE_MAPS_API_KEY},
    )


def contact_us(request):
    return render(
        request,
        "transit_hub/contact.html",
        {"google_maps_api_key": settings.GOOGLE_MAPS_API_KEY},
    )


def view_bus(request):
    # Get distinct schedules with related information
    schedules = Transportation_schedules.objects.select_related(
        "bus", "route", "driver"
    ).distinct()

    buses_data = []
    for schedule in schedules:
        # Get stoppages for this route
        route_stoppages = (
            RouteStoppageModel.objects.filter(route=schedule.route)
            .select_related("stoppage")
            .order_by("-created_at")
        )

        stoppage_names = [rs.stoppage.stoppage_name for rs in route_stoppages]

        buses_data.append(
            {
                "bus_name": schedule.bus.bus_name,
                "bus_capacity": schedule.bus.bus_capacity,
                "bus_tag": schedule.bus.bus_tag,
                "route_name": schedule.route.route_name,
                "driver_name": schedule.driver.name,
                "stoppages": stoppage_names,
                "departure_time": schedule.departure_time.strftime("%I:%M %p"),
                "days": schedule.days,
            }
        )

    context = {
        "buses": buses_data,
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
    }

    return render(request, "transit_hub/view_bus.html", context)


@csrf_exempt
def get_bus_location(request, bus_name):
    """Get real-time location data for a specific bus"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        # Get the bus
        bus = Bus.objects.get(bus_name=bus_name)

        # Get the most recent location data
        location_data = (
            LocationData.objects.filter(bus=bus).order_by("-timestamp").first()
        )
        if not location_data:
            return JsonResponse(
                {
                    "success": False,
                    "message": "No location data found for this bus",
                    "is_moving": False,
                }
            )

        # Check if data is recent (within last 2 minutes)
        time_threshold = timezone.now() - timedelta(minutes=2)
        is_recent = location_data.timestamp > time_threshold

        # Check if bus is moving by comparing with previous location
        is_moving = False
        previous_location = (
            LocationData.objects.filter(bus=bus, timestamp__lt=location_data.timestamp)
            .order_by("-timestamp")
            .first()
        )

        if previous_location and is_recent:
            # Calculate distance between current and previous location
            lat_diff = abs(location_data.latitude - previous_location.latitude)
            lng_diff = abs(location_data.longitude - previous_location.longitude)
            # If coordinates changed by more than 0.0001 degrees (~10 meters), consider it moving
            is_moving = (lat_diff > 0.0001) or (lng_diff > 0.0001)

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "latitude": location_data.latitude,
                    "longitude": location_data.longitude,
                    "timestamp": location_data.timestamp.isoformat(),
                    "last_updated": location_data.timestamp.strftime("%I:%M %p"),
                    "is_recent": is_recent,
                    "is_moving": is_moving,
                    "bus_name": bus.bus_name,
                    "driver_name": (
                        location_data.driver.name if location_data.driver else "Unknown"
                    ),
                },
            }
        )

    except Bus.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Bus not found", "is_moving": False}
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": "Internal server error", "is_moving": False}
        )


def get_all_stoppages(request):
    """
    API endpoint to get all stoppages for session storage
    """
    stoppages = (
        Stoppage.objects.filter(stoppage_status=True)
        .values("id", "stoppage_name")
        .order_by("stoppage_name")
    )

    return JsonResponse({"stoppages": list(stoppages)})
