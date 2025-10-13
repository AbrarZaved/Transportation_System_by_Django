import time
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import Preference, Student
from transit_hub.models import Route
from django.http import JsonResponse
import json
from transit_hub.serializer import RouteSerializer, RouteStoppageSerializer
from transport_manager.models import Transportation_schedules
from .models import RouteStoppage as RouteStoppageModel
from django.db.models import F
from django.shortcuts import render
from django.utils.timezone import localtime


def format_time(dt):
    return dt.strftime("%I:%M %p")  # e.g., 08:30 AM


def index(request):
    user = request.session.get("student_id")
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
            Preference.objects.filter(student__student_id=user).order_by("-created_at")[
                :3
            ]
        )

    return render(
        request,
        "transit_hub/index.html",
        {
            "preferences": preferences,
            "popular_routes": data,
        },
    )


@sync_to_async
def get_schedules(trip_type, place, student_id=None):
    from django.db.models import Q

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
                    if student_id
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
def save_preference_by_session(student_id, place):
    student = Student.objects.filter(student_id=student_id).first()

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


async def search_route(request):
    if request.method == "POST":
        start_time = time.time()
        body = json.loads(request.body)
        trip_type = body.get("tripType")
        place = body.get("place")
        student_id = body.get("studentId")
        data = await get_schedules(trip_type, place, student_id)

        try:
            if data and student_id:
                await save_preference_by_session(student_id, place)
        except Exception as e:
            print(e)
        end_time = time.time()
        print((end_time - start_time) * 1000)
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
    return render(request, "transit_hub/about.html")


def contact_us(request):
    return render(request, "transit_hub/contact.html")


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

    return render(request, "transit_hub/view_bus.html", {"buses": buses_data})


def get_all_stoppages(request):
    """
    API endpoint to get all stoppages for session storage
    """
    from .models import Stoppage

    stoppages = (
        Stoppage.objects.filter(stoppage_status=True)
        .values("id", "stoppage_name")
        .order_by("stoppage_name")
    )

    return JsonResponse({"stoppages": list(stoppages)})
