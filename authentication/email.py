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
