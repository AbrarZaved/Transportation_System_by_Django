from django.conf import settings


def google_maps_context(request):
    """
    Context processor to provide Google Maps API key to templates
    """
    return {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}
