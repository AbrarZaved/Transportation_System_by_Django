from django.shortcuts import render

# Create your views here.
def subscription(request):
    # This view will handle the subscription logic
    return render(request, 'transport_manager/subscription.html')