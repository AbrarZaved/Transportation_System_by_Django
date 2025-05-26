import requests
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def my_account(request):

    # profile = requests.get(
    #     "http://peoplepulse.diu.edu.bd:8189/result/studentInfo?studentId=221-15-5053"
    # )
    # print(profile.json())
    return render(request, "authentication/my_account.html")
