from rest_framework import serializers

from transit_hub.models import Route, RouteStoppage


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"


class RouteStoppageSerializer(serializers.ModelSerializer):
    stoppage_name = serializers.CharField(source="stoppage.stoppage_name")

    class Meta:
        model = RouteStoppage
        fields = ["id", "created_at", "route", "stoppage", "stoppage_name"]
