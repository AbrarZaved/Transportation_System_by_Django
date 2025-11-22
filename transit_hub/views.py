from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from social_core.backends import username
from authentication.models import Preference, Student, Review
from transit_hub.models import Route
from django.http import JsonResponse
import json
from transit_hub.serializer import RouteSerializer, RouteStoppageSerializer
from transport_manager.models import Transportation_schedules
from .models import RouteStoppage as RouteStoppageModel
from django.db.models import F
from django.shortcuts import render
from django.utils.timezone import localtime
from django.db.models import Q
from .models import Stoppage
from django.conf import settings


def format_time(dt):
    return dt.strftime("%I:%M %p")  # e.g., 08:30 AM


def index(request):
    user = request.session.get("username")
    preferences = []
    current_time = localtime().time()
    current_day = localtime().strftime("%A").lower()

    data = cache.get("popular_routes")
    if data is None:
        places = ["dhanmondi", "mirpur", "uttara"]
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
            formatted = [(bus, format_time(departure)) for bus, departure in schedules]
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
