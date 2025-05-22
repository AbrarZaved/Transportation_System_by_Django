
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def my_account(request):
    return render(request, "authentication/my_account.html")