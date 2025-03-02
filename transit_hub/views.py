from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from transit_hub.models import Route
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from transit_hub.serializer import RouteSerializer, RouteStoppageSerializer
from .models import RouteStoppage as RouteStoppageModel


def index(request):
    routes = Route.objects.all()
    # for route in routes:
    #     print(f"Route: {route.route_name}")
    #     print("Stopages:", route.route_details.all())  # Debugging
    return render(request, "transit_hub/index.html", {"routes": routes})


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
