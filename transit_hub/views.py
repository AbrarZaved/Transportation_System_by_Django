from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from social_core.backends import username
from authentication.models import Preference, Student, Review
from transit_hub.models import Route, Bus
from django.http import JsonResponse
import json
from transit_hub.serializer import RouteSerializer, RouteStoppageSerializer
from transport_manager.models import Transportation_schedules, LocationData
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

    data = cache.get("popular_routes")
    if data is None:
        places = ["dhanmondi", "mirpur", "uttara", "tongi"]
        data = {}
        for place in places:
            schedules = (
                Transportation_schedules.objects.filter(
                    from_dsc=True,
                    route__route_name__icontains=place,
                    departure_time__gte=current_time,
                    days__contains=current_day,
                )
                .values_list("bus__bus_name", "departure_time")
                .distinct()
            )
            formatted = [
                (bus, (departure.strftime("%I:%M %p"))) for bus, departure in schedules
            ]
            data[place] = formatted

        cache.set("popular_routes", data, timeout=60)
    if user:
        preferences = list(
            Preference.objects.filter(student__username=user).order_by("-created_at")[
                :3
            ]
        )

    # Get recent reviews for carousel (4+ star reviews)
    try:
        recent_reviews = (
            Review.objects.select_related("student", "bus", "route")
            .filter(is_approved=True, rating__gte=4)
            .order_by("-created_at")[:6]
        )

        reviews_data = []
        for review in recent_reviews:
            target_name = review.bus.bus_name if review.bus else review.route.route_name
            target_type = "Bus" if review.bus else "Route"

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
        # Fallback if Review model doesn't exist or there's an error
        reviews_data = []

    return render(
        request,
        "transit_hub/index.html",
        {
            "preferences": preferences,
            "popular_routes": data,
            "recent_reviews": reviews_data,
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        },
    )


@sync_to_async
def get_schedules(trip_type, place, username=None):

    # Search for routes by both route name and stoppage name
    schedules = (
        Transportation_schedules.objects.select_related("bus", "driver", "route")
        .filter(
            Q(route__route_name__icontains=place)
            | Q(route__routestoppage__stoppage__stoppage_name__icontains=place),
            from_dsc=(trip_type == "From DSC"),
            departure_time__gte=localtime().time(),
            days__contains=localtime().strftime("%A").lower(),
        )
        .distinct()
    )  # Add distinct to avoid duplicates from JOIN
    route_ids = schedules.values_list("route__id", flat=True).distinct()
    route_details = RouteStoppageModel.objects.filter(route_id__in=route_ids)

    stoppages_by_route = {}
    for stop in route_details:
        stoppages_by_route.setdefault(stop.route_id, []).append(stop)

    data = []
    for schedule in schedules:
        route_obj = schedule.route
        route_id = route_obj.id

        data.append(
            {
                "route": RouteSerializer(route_obj).data,
                "route_name": route_obj.route_name,
                "audience": schedule.get_audience_display(),
                "departure_time": (
                    schedule.departure_time.strftime("%I:%M %p")
                    if username
                    else "Available"
                ),
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
