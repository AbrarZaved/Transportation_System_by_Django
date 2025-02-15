from django.shortcuts import render

from transit_hub.models import Route
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import RouteStoppage, Stoppage


def index(request):
    routes = Route.objects.all()
    print(routes)
    # for route in routes:
    #     print(f"Route: {route.route_name}")
    #     print("Stopages:", route.route_details.all())  # Debugging
    return render(request, "transit_hub/index.html", {"routes": routes})
