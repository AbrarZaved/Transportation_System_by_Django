from email import message
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib import messages


# Create your views here.
def subscription(request):
    return render(request, "transport_manager/subscription.html")


def admin_login(request):
    if request.method == "POST":
        # Handle the login logic here
        employee_id = request.POST.get("employee_id")
        password = request.POST.get("password")
        user = authenticate(request, employee_id=employee_id, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid Employee ID or Password.")
            return redirect("diu_admin")
    return render(request, "transport_manager/admin_login.html")


def dashboard(request):
    return render(request, "transport_manager/dashboard.html")


def admin_logout(request):
    # Handle the logout logic here
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("diu_admin")