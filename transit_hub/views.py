import time
from asgiref.sync import sync_to_async
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
import sys, os
from django.shortcuts import render
import requests


def index(request):
    user = request.session.get("student_id")
    print("User ID:", user)
    if user:
        preferences = Preference.objects.filter(student__student_id=user).order_by(
            "-total_searches"
        )[:3]
        return render(request, "transit_hub/index.html", {"preferences": preferences})
    return render(request, "transit_hub/index.html")


@sync_to_async
def get_schedules(trip_type, place):

    schedules = Transportation_schedules.objects.select_related(
        "bus", "driver", "route"
    ).filter(from_dsc=(trip_type == "From DSC"), route__route_name__icontains=place)

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
                "departure_time": schedule.departure_time,
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
                    "name": f"{schedule.driver.first_name} {schedule.driver.last_name}",
                    "phone_number": schedule.driver.phone_number,
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
            total_searches=F("total_searches") + 1,
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
        data = await get_schedules(trip_type, place)

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
