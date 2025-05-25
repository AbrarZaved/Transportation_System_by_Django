import time
from asgiref.sync import sync_to_async
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from transit_hub.models import Route
from django.http import JsonResponse
import json
from transit_hub.serializer import RouteSerializer, RouteStoppageSerializer
from transport_manager.models import Transportation_schedules
from .models import RouteStoppage as RouteStoppageModel


def index(request):
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


async def search_route(request):
    if request.method == "POST":
        start_time=time.time()
        body = json.loads(request.body)
        trip_type = body.get("tripType")
        place = body.get("place")

        data = await get_schedules(trip_type, place)
        end_time=time.time()
        print((end_time-start_time) *1000)
        return JsonResponse({"routes": data})


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
