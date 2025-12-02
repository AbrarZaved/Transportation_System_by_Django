from functools import wraps
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.db import models
from django.forms import ValidationError
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status
from authentication.email import (
    create_email_otp,
    send_otp_email,
    send_support_ticket_generated_email,
    send_support_ticket_updated_email,
)
from authentication.forms import SupportTicketForm
from authentication.models import (
    EmailOTP,
    Preference,
    Student,
    StudentReview,
    SupportTicket,
)
from threading import Thread
from authentication.models import DriverAuth
from transit_hub.models import Bus, Route, Driver
from django.core.paginator import Paginator
from django.db.models import Avg
from transit_hub.models import Bus, Route
from django.core.paginator import Paginator
from django.db.models import Avg


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def student_wrapper(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        username = request.session.get("username")
        student = get_object_or_404(Student, username=username)
        if student.verified or not username:
            return redirect("index")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


@student_wrapper
def verify_otp_view(request):
    if request.method == "POST":
        otp_input = json.loads(request.body).get("otp")
        otp_obj = EmailOTP.objects.filter(otp=otp_input).last()

        if otp_obj and not otp_obj.is_expired():
            otp_obj.user.verified = True
            otp_obj.user.save()
            request.session["username"] = otp_obj.user.username
            request.session["is_student_authenticated"] = True
            messages.success(request, "Email verified successfully!")
            return JsonResponse({"success": True})
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, "authentication/verify_otp.html")


@csrf_exempt
def resend_otp(request):
    if request.method == "POST":
        try:
            username = request.session.get("username")
            if not username:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Session expired. Please register again.",
                    },
                    status=400,
                )

            try:
                student = Student.objects.get(username=username)
                if student.verified:
                    return JsonResponse(
                        {"success": False, "message": "Account already verified."},
                        status=400,
                    )
            except Student.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "Student not found."}, status=400
                )

            # Delete any existing OTPs for this user
            EmailOTP.objects.filter(user=student).delete()

            # Create and send new OTP
            otp = create_email_otp(student)
            email_thread = Thread(target=send_otp_email, args=(student, otp))
            email_thread.daemon = True
            email_thread.start()

            return JsonResponse(
                {
                    "success": True,
                    "message": "New OTP has been sent to your email address.",
                }
            )

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Failed to resend OTP. Please try again.",
                },
                status=500,
            )

    return JsonResponse(
        {"success": False, "message": "Invalid request method."}, status=405
    )


def my_account(request):
    username = request.session.get("username")
    if not username:
        return redirect("index")

    student = get_object_or_404(Student, username=username)
    total_searches = (
        Preference.objects.filter(student=student)
        .aggregate(total_searches=models.Sum("total_searches"))
        .get("total_searches", 0)
    )
    return render(
        request,
        "authentication/my_account.html",
        {"student": student, "total_searches": total_searches if total_searches else 0},
    )


def login_request(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        password = request.POST.get("password", "").strip()

        if not student_id or not password:
            messages.error(request, "Please provide both Student ID and password.")
            return redirect("index")

        student = Student.objects.filter(student_id=student_id, verified=True).first()

        if not student:
            messages.error(request, "Student ID not found or account not verified.")
            return redirect("index")

        if not student.check_password(password):
            messages.error(request, "Incorrect password. Please try again.")
            return redirect("index")

        # Login successful
        request.session["username"] = student.username
        request.session["is_student_authenticated"] = True
        request.session.set_expiry(3600)  # 1 hour

        # Create login activity record (location will be updated via AJAX)
        from authentication.models import StudentLoginActivity

        login_activity = StudentLoginActivity.objects.create(
            student=student,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        request.session["login_activity_id"] = login_activity.id
        request.session["location_tracked"] = False  # Reset flag for new login

        messages.success(request, "Logged In!", extra_tags=student.name)
        return redirect("index")

    return redirect("index")


@csrf_exempt
def update_login_location(request):
    """Update login location via AJAX after user approves geolocation"""
    if request.method == "POST":
        try:
            from geopy.geocoders import Nominatim

            data = json.loads(request.body)
            login_activity_id = request.session.get("login_activity_id")

            if not login_activity_id:
                return JsonResponse(
                    {"success": False, "message": "No active login session"}
                )

            from authentication.models import StudentLoginActivity

            login_activity = StudentLoginActivity.objects.filter(
                id=login_activity_id
            ).first()

            if login_activity:
                latitude = data.get("latitude")
                longitude = data.get("longitude")

                # Convert coordinates to readable address
                try:
                    geolocator = Nominatim(user_agent="bahon-location-service")
                    location = geolocator.reverse(
                        f"{latitude}, {longitude}", language="en"
                    )
                    print(location.address)
                    login_activity.location = (
                        location.address
                        if location
                        else f"Lat: {latitude}, Lon: {longitude}"
                    )
                except Exception as e:
                    # If geocoding fails, store coordinates as fallback
                    login_activity.location = f"Lat: {latitude}, Lon: {longitude}"

                login_activity.save()
                return JsonResponse({"success": True})

            return JsonResponse(
                {"success": False, "message": "Login activity not found"}
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})


@csrf_exempt
def check_login_session(request):
    """Check if there's a fresh login session that needs location tracking"""
    login_activity_id = request.session.get("login_activity_id")
    location_tracked = request.session.get("location_tracked", False)

    if login_activity_id and not location_tracked:
        # Mark as tracked to avoid repeated requests
        request.session["location_tracked"] = True
        return JsonResponse({"should_track": True})

    return JsonResponse({"should_track": False})


def register_request(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        password = request.POST.get("password", "").strip()
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()

        # Validate required fields
        if not all([student_id, password, name, email, phone_number]):
            messages.error(request, "All fields are required.")
            return redirect("index")

        # Check if student ID already exists
        if Student.objects.filter(student_id=student_id).exists():
            messages.error(
                request, "Student ID already exists. Please use a different ID."
            )
            return redirect("index")

        # Check if email already exists
        if Student.objects.filter(email=email).exists():
            messages.error(
                request, "Email already registered. Please use a different email."
            )
            return redirect("index")

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect("index")

        # Validate password length
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect("index")

        try:
            student = Student(
                student_id=student_id,
                name=name,
                email=email,
                phone_number=phone_number,
            )
            student.set_password(password)
            student.save()
            request.session["username"] = student.username

            # Send OTP asynchronously using threading
            otp = create_email_otp(student)
            email_thread = Thread(target=send_otp_email, args=(student, otp))
            email_thread.daemon = True  # Thread will die when main program exits
            email_thread.start()

            messages.success(
                request,
                "Registration successful! Please check your email for OTP verification.",
            )
            return redirect("verify_otp")
        except Exception as e:
            messages.error(request, "Registration failed. Please try again.")
            return redirect("index")

    return redirect("index")


def sign_out(request):
    request.session.flush()
    messages.success(request, "Logged Out!")
    return redirect("index")


def get_history(request):
    try:
        if request.method == "POST":
            username = request.session.get("username")
            student = Student.objects.filter(username=username).first()
            if not student:
                return JsonResponse({"history": []})

            history_qs = Preference.objects.filter(student=student).order_by(
                "-created_at"
            )
            history = [
                {"id": item.id, "place": item.searched_locations} for item in history_qs
            ]
            return JsonResponse({"history": history})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)


@csrf_exempt
def delete_history(request, id):
    if request.method == "DELETE":
        Preference.objects.filter(id=id).delete()
        return JsonResponse({"status": "deleted"})
    return JsonResponse({"error": "Invalid method"}, status=405)


def edit_profile(request):
    if request.method == "POST":
        username = request.session.get("username")
        student = get_object_or_404(Student, username=username)

        # Fields to check in POST
        fields = ["name", "phone_number", "dept_name", "batch_code", "student_id"]

        for field in fields:
            value = request.POST.get(field, "").strip()
            if value and value != getattr(student, field):
                setattr(student, field, value)

        # Handle profile picture separately
        profile_pic = request.FILES.get("profile_pic")
        if profile_pic:
            student.profile_pic = profile_pic

        student.save()
        messages.success(request, "Your profile has been updated successfully.")
        return redirect("my_account")


def social_auth_error(request):
    messages.error(request, "Not Allowed")
    return redirect("index")


def admin_login(request):
    if request.method == "POST":
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


def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("diu_admin")


def driver_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            device_id = data.get("device_id")

            # Validate required fields
            if not username or not password or not device_id:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Username, password, and device_id are required.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = DriverAuth.objects.filter(username=username).first()

            if user:
                password_valid = user.check_password(password)
                if password_valid:
                    if not user.device_id:
                        user.device_id = device_id
                    else:
                        if user.device_id != device_id:
                            return JsonResponse(
                                {
                                    "success": False,
                                    "message": "Device not recognized. Please contact admin.",
                                },
                                status=status.HTTP_403_FORBIDDEN,
                            )
                    user.last_login = now()
                    # Prevent re-hashing password on save
                    user._password_changed = False
                    user.save(update_fields=["device_id", "last_login"])
                    return JsonResponse(
                        {
                            "success": True,
                            "auth_token": user.auth_token,
                            "driver_id": user.driver.id,
                        }
                    )
                else:
                    print("Password check failed")
                    return JsonResponse(
                        {"success": False, "message": "Invalid credentials."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            else:
                print("User not found")
                return JsonResponse(
                    {"success": False, "message": "Invalid credentials."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except json.JSONDecodeError:
            return JsonResponse(
                {"success": False, "message": "Invalid JSON data."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(f"Login error: {str(e)}")
            return JsonResponse(
                {"success": False, "message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        return JsonResponse(
            {"success": False, "message": "Invalid request method."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


def reviews_page(request):
    """Display all reviews with filtering and pagination"""
    username = request.session.get("username")

    # Get filter parameters
    filter_type = request.GET.get("filter", "all")  # all, bus, driver
    search_query = request.GET.get("search", "")

    # Base queryset
    reviews = StudentReview.objects.select_related("student", "bus", "driver").filter(
        is_approved=True
    )

    # Apply filters
    if filter_type == "bus":
        reviews = reviews.filter(bus__isnull=False)
    elif filter_type == "driver":
        reviews = reviews.filter(driver__isnull=False)

    # Apply search
    if search_query:
        reviews = reviews.filter(
            models.Q(bus__bus_name__icontains=search_query)
            | models.Q(driver__name__icontains=search_query)
            | models.Q(student__name__icontains=search_query)
            | models.Q(comment__icontains=search_query)
        )

    # Calculate statistics
    all_reviews = StudentReview.objects.filter(is_approved=True)
    total_reviews = all_reviews.count()
    average_rating = (
        all_reviews.aggregate(avg_rating=models.Avg("rating"))["avg_rating"] or 0
    )

    # Get current month's reviews
    from datetime import datetime

    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_reviews = all_reviews.filter(
        created_at__month=current_month, created_at__year=current_year
    ).count()

    # Pagination
    paginator = Paginator(reviews, 12)  # 12 reviews per page
    page_number = request.GET.get("page")
    reviews_page_obj = paginator.get_page(page_number)

    # Get available buses and drivers for the review form
    buses = Bus.objects.all().order_by("bus_name")
    drivers = Driver.objects.filter(driver_status=True).order_by("name")

    # Serialize data for JavaScript
    buses_data = [
        {"id": bus.id, "bus_name": bus.bus_name, "bus_tag": bus.bus_tag}
        for bus in buses
    ]

    drivers_data = [{"id": driver.id, "driver_name": driver.name} for driver in drivers]

    context = {
        "reviews": reviews_page_obj,
        "buses": json.dumps(buses_data),
        "drivers": json.dumps(drivers_data),
        "filter_type": filter_type,
        "search_query": search_query,
        "is_authenticated": bool(username),
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "monthly_reviews": monthly_reviews,
    }

    return render(request, "authentication/reviews.html", context)


@csrf_exempt
def submit_review(request):
    """Submit a new review"""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    username = request.session.get("username")
    if not username:
        return JsonResponse(
            {"success": False, "message": "Please login to submit a review"}, status=401
        )

    try:
        student = Student.objects.get(username=username)
    except Student.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Student not found"}, status=404
        )

    try:
        data = json.loads(request.body)
        review_type = data.get("review_type")  # 'bus' or 'driver'
        bus_id = data.get("bus_id")
        driver_id = data.get("driver_id")
        rating = data.get("rating")
        comment = data.get("comment", "").strip()

        # Validation
        if not all([review_type, rating, comment]):
            return JsonResponse(
                {"success": False, "message": "All fields are required"}, status=400
            )

        if review_type not in ["bus", "driver"]:
            return JsonResponse(
                {"success": False, "message": "Invalid review type"}, status=400
            )

        # Validate IDs based on review type
        if review_type == "bus" and not bus_id:
            return JsonResponse(
                {"success": False, "message": "Bus ID is required for bus review"},
                status=400,
            )
        elif review_type == "driver" and not driver_id:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Driver ID is required for driver review",
                },
                status=400,
            )

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            return JsonResponse(
                {"success": False, "message": "Rating must be between 1 and 5"},
                status=400,
            )

        if len(comment) < 10:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Comment must be at least 10 characters long",
                },
                status=400,
            )

        # Get target objects
        bus = None
        driver = None

        if review_type == "bus" and bus_id:
            try:
                bus = Bus.objects.get(id=bus_id)
            except Bus.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "Bus not found"}, status=404
                )

        if review_type == "driver" and driver_id:
            try:
                driver = Driver.objects.get(id=driver_id)
            except Driver.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "Driver not found"}, status=404
                )

        # Check if review already exists
        existing_review = StudentReview.objects.filter(
            student=student, bus=bus, driver=driver
        ).first()

        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            message = "Review updated successfully!"
        else:
            # Create new review
            StudentReview.objects.create(
                student=student, bus=bus, driver=driver, rating=rating, comment=comment
            )
            message = "Review submitted successfully!"

        return JsonResponse({"success": True, "message": message})

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "Invalid JSON data"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": "Internal server error"}, status=500
        )


@csrf_exempt
def delete_review(request, review_id):
    """Delete a user's review"""
    if request.method != "DELETE":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    username = request.session.get("username")
    if not username:
        return JsonResponse(
            {"success": False, "message": "Please login to delete review"}, status=401
        )

    try:
        student = Student.objects.get(username=username)
        review = StudentReview.objects.get(id=review_id, student=student)
        review.delete()
        return JsonResponse(
            {"success": True, "message": "Review deleted successfully!"}
        )
    except Student.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Student not found"}, status=404
        )
    except Review.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Review not found"}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": "Internal server error"}, status=500
        )


def get_reviews_for_carousel(request):
    """Get recent reviews for the index page carousel"""
    reviews = (
        StudentReview.objects.select_related("student", "bus", "driver")
        .filter(
            is_approved=True, rating__gte=4  # Only show 4+ star reviews in carousel
        )
        .order_by("-created_at")[:6]
    )

    reviews_data = []
    for review in reviews:
        target_name = review.bus.bus_name if review.bus else review.driver.name
        target_type = "Bus" if review.bus else "Driver"

        reviews_data.append(
            {
                "id": review.id,
                "student_name": review.student.name,
                "target_name": target_name,
                "target_type": target_type,
                "rating": review.rating,
                "comment": (
                    review.comment[:100] + "..."
                    if len(review.comment) > 100
                    else review.comment
                ),
                "created_at": review.created_at.strftime("%B %d, %Y"),
            }
        )

    return JsonResponse({"reviews": reviews_data})


def contact_us(request):
    form = SupportTicketForm()
    if request.method == "POST":
        print("Received POST request for contact us")
        username = request.session.get("username")
        if username:
            student = get_object_or_404(Student, username=username)
            form = SupportTicketForm(request.POST, request.FILES)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.student = student
                ticket.save()
                email_thread = Thread(
                    target=send_support_ticket_generated_email, args=(student, ticket)
                )
                email_thread.daemon = True  # Thread will die when main program exits
                email_thread.start()
                messages.success(
                    request, f"Ticket {ticket.ticket_id} created successfully!"
                )
                return redirect("ticket_detail", ticket_id=ticket.ticket_id)
            else:
                messages.error(request, "Please fill all required fields correctly.")
        else:
            messages.error(request, "Please login to submit a ticket.")
            return redirect("index")
    return render(request, "authentication/contact.html", {"form": form})


# Support Ticket Views
def support_tickets(request):
    form = SupportTicketForm()
    """View for students to manage their support tickets"""
    username = request.session.get("username")
    if not username:
        messages.error(request, "Please login to view your support tickets.")
        return redirect("index")

    student = get_object_or_404(Student, username=username)

    # Get filter parameters
    status_filter = request.GET.get("status", "all")
    category_filter = request.GET.get("category", "all")

    # Base query
    tickets = student.support_tickets.all()

    # Apply filters
    if status_filter != "all":
        tickets = tickets.filter(status=status_filter)
    if category_filter != "all":
        tickets = tickets.filter(category=category_filter)

    # Pagination
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    from authentication.models import SupportTicket

    context = {
        "tickets": page_obj,
        "student": student,
        "status_choices": SupportTicket.STATUS_CHOICES,
        "category_choices": SupportTicket.CATEGORY_CHOICES,
        "current_status": status_filter,
        "current_category": category_filter,
        "form": form,
    }

    return render(request, "authentication/support_tickets.html", context)


def create_ticket(request):
    """Create a new support ticket"""

    username = request.session.get("username")
    if not username:
        return JsonResponse({"success": False, "error": "Not authenticated"})

    student = get_object_or_404(Student, username=username)
    if request.method == "POST":
        form = SupportTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.student = student
            ticket.save()
            email_thread = Thread(
                target=send_support_ticket_generated_email, args=(student, ticket)
            )
            email_thread.daemon = True  # Thread will die when main program exits
            email_thread.start()
            messages.success(
                request, f"Ticket {ticket.ticket_id} created successfully!"
            )
            return redirect("ticket_detail", ticket_id=ticket.ticket_id)
        else:
            messages.error(
                request,
                "There was an error with your submission. Please check the form and try again.",
            )
            return redirect("support_tickets")

    return redirect("support_tickets")


def ticket_detail(request, ticket_id):
    """View ticket details"""
    username = request.session.get("username")
    if not username:
        messages.error(request, "Please login to view ticket details.")
        return redirect("login")

    student = get_object_or_404(Student, username=username)
    ticket = get_object_or_404(student.support_tickets, ticket_id=ticket_id)

    context = {
        "ticket": ticket,
        "student": student,
    }

    return render(request, "authentication/ticket_detail.html", context)


# Admin Support Ticket Views
@login_required(login_url="diu_admin")
def admin_support_tickets(request):
    """Admin view for managing all support tickets with filtering and stats"""
    # Get filter parameters
    status_filter = request.GET.get("status", "all")
    category_filter = request.GET.get("category", "all")
    assigned_filter = request.GET.get("assigned", "all")

    # Base query
    tickets = SupportTicket.objects.all()

    # Apply filters
    if status_filter != "all":
        tickets = tickets.filter(status=status_filter)
    if category_filter != "all":
        tickets = tickets.filter(category=category_filter)
    if assigned_filter == "me":
        tickets = tickets.filter(assigned_to=request.user)
    elif assigned_filter == "unassigned":
        tickets = tickets.filter(assigned_to__isnull=True)

    # Statistics
    stats = {
        "total": SupportTicket.objects.count(),
        "open": SupportTicket.objects.filter(status="open").count(),
        "in_progress": SupportTicket.objects.filter(status="in_progress").count(),
        "resolved": SupportTicket.objects.filter(status="resolved").count(),
    }

    # Pagination
    paginator = Paginator(tickets, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "tickets": page_obj,
        "stats": stats,
        "status_choices": SupportTicket.STATUS_CHOICES,
        "category_choices": SupportTicket.CATEGORY_CHOICES,
        "current_status": status_filter,
        "current_category": category_filter,
        "current_assigned": assigned_filter,
    }

    return render(request, "transport_manager/support_tickets.html", context)


def admin_ticket_detail(request, ticket_id):
    """Admin view for ticket details with full controls"""
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect("admin_login")

    from authentication.models import SupportTicket, TicketMessage, Supervisor

    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_note":
            note_text = request.POST.get("note")
            if note_text:
                TicketMessage.objects.create(
                    ticket=ticket,
                    sender_supervisor=request.user,
                    message=note_text,
                    is_internal=True,
                )
                ticket.updated_at = now()
                ticket.save()
                messages.success(request, "Note added successfully!")

        elif action == "update_status":
            new_status = request.POST.get("status")
            if new_status:
                ticket.status = new_status
                if new_status == "resolved":
                    ticket.resolved_at = now()
                ticket.save()
                send_support_ticket_updated_email(ticket.student, ticket)
                messages.success(request, f"Ticket status updated to {new_status}!")

        elif action == "assign":
            supervisor_id = request.POST.get("assigned_to")
            if supervisor_id:
                supervisor = get_object_or_404(Supervisor, id=supervisor_id)
                ticket.assigned_to = supervisor
                ticket.save()
                messages.success(
                    request, f"Ticket assigned to {supervisor.first_name}!"
                )

        return redirect("admin_ticket_detail", ticket_id=ticket_id)

    supervisors = Supervisor.objects.filter(is_staff=True)

    context = {
        "ticket": ticket,
        "admin_notes": ticket.messages.filter(is_internal=True),
        "supervisors": supervisors,
        "status_choices": SupportTicket.STATUS_CHOICES,
    }

    return render(request, "admin_kits/ticket_detail.html", context)


@login_required(login_url="diu_admin")
def student_reports(request):
    """Admin view for student activity reports"""
    from authentication.models import StudentLoginActivity
    from django.db.models import Count, Q

    # Get all students with their statistics
    students = Student.objects.annotate(
        total_logins=Count("login_activities"),
        total_searches=models.Sum("preference__total_searches"),
    ).order_by("-total_logins")

    # Get filter parameters
    student_filter = request.GET.get("student_id", "")

    # Filter by specific student if requested
    if student_filter:
        students = students.filter(student_id=student_filter)

    # Pagination for students list
    paginator = Paginator(students, 20)
    page_number = request.GET.get("page")
    students_page = paginator.get_page(page_number)

    # Overall statistics
    total_students = Student.objects.count()
    total_logins = StudentLoginActivity.objects.count()
    students_with_location = (
        StudentLoginActivity.objects.filter(location__isnull=False)
        .exclude(location="")
        .values("student")
        .distinct()
        .count()
    )

    context = {
        "students": students_page,
        "total_students": total_students,
        "total_logins": total_logins,
        "students_with_location": students_with_location,
        "current_filter": student_filter,
    }

    return render(request, "transport_manager/student_reports.html", context)


@login_required(login_url="diu_admin")
def student_report_detail(request, student_id):
    """Detailed report for a specific student"""
    from authentication.models import StudentLoginActivity
    from django.db.models import Count

    student = get_object_or_404(Student, student_id=student_id)

    # Get login activities
    login_activities = student.login_activities.all()[:50]  # Last 50 logins

    # Get first and last login for summary (before slicing)
    all_logins = student.login_activities.all()
    first_login = all_logins.first()
    last_login = all_logins.last()

    # Get search preferences with counts
    preferences = Preference.objects.filter(student=student).order_by(
        "-total_searches"
    )[:10]

    # Calculate statistics
    total_logins = student.login_activities.count()
    logins_with_location = (
        student.login_activities.filter(location__isnull=False)
        .exclude(location="")
        .count()
    )

    total_searches = (
        Preference.objects.filter(student=student).aggregate(
            total=models.Sum("total_searches")
        )["total"]
        or 0
    )

    unique_locations_searched = Preference.objects.filter(student=student).count()

    # Get most searched location
    most_searched = preferences.first()

    # Recent login activity (last 7 days)
    from datetime import timedelta

    seven_days_ago = now() - timedelta(days=7)
    recent_logins = student.login_activities.filter(
        login_time__gte=seven_days_ago
    ).count()

    context = {
        "student": student,
        "login_activities": login_activities,
        "first_login": first_login,
        "last_login": last_login,
        "preferences": preferences,
        "total_logins": total_logins,
        "logins_with_location": logins_with_location,
        "total_searches": total_searches,
        "unique_locations_searched": unique_locations_searched,
        "most_searched": most_searched,
        "recent_logins": recent_logins,
    }

    return render(request, "transport_manager/student_report_detail.html", context)
