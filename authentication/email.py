import random
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from authentication.models import EmailOTP



def generate_otp():
    return str(random.randint(100000, 999999))


def create_email_otp(user):
    otp_code = generate_otp()
    EmailOTP.objects.create(
        user=user, otp=otp_code, expires_at=now() + timedelta(minutes=5)
    )
    return otp_code


def send_otp_email(user, otp):
    subject = "Bahon Email Verification"
    message = f"Your OTP is: {otp}. It will expire in 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def humanize_text(text):
    return text.replace("_", " ").capitalize()

def send_support_ticket_generated_email(student, ticket):
    subject = f"Support Ticket Created: {ticket.ticket_id}"
    message = (
        f"Dear {student.name},\n\n"
        f"Your support ticket has been created successfully.\n"
        f"Ticket ID: {ticket.ticket_id}\n"
        f"Subject: {ticket.subject}\n"
        f"Category: {humanize_text(ticket.category)}\n"
        f"Status: {humanize_text(ticket.status)}\n\n"
        "We will get back to you shortly.\n\n"
        "Best regards,\n"
        "Bahon Transport Support Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student.email])

def send_support_ticket_updated_email(student, ticket):
    subject = f"Support Ticket Updated: {ticket.ticket_id}"
    message = (
        f"Dear {student.name},\n\n"
        f"Your support ticket has been updated.\n"
        f"Ticket ID: {ticket.ticket_id}\n"
        f"Subject: {ticket.subject}\n"
        f"Category: {humanize_text(ticket.category)}\n"
        f"Status: {humanize_text(ticket.status)}\n\n"
        "We will keep you informed of any further updates.\n\n"
        "Best regards,\n"
        "Bahon Transport Support Team"
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student.email])