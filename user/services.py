from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import Permission
from django.db import IntegrityError, transaction
from django.conf import settings
from core.exceptions import CustomException
from user.models import User


class UserService:
    @staticmethod
    def login(request, validated_data):
        user = User.objects.filter(email=validated_data.get("email")).first()
        if not user:
            raise CustomException(detail="Email or Password is not correct", status_code=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(validated_data.get("password")):
            raise CustomException(detail="Email or Password is not correct", status_code=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            raise CustomException(detail="User is not active", status_code=status.HTTP_400_BAD_REQUEST)
        # authenticate(request, email=email, password=password)
        refresh = RefreshToken.for_user(user)
        data = {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_image": str(user.profile_image.url) if user.profile_image else None,
            "role": user.groups.first().name,
            "permissions": user.groups.first().permissions.values_list("codename", flat=True),
        }
        return data

    @staticmethod
    def send_password_reset_email(email):
        user = User.objects.get(email=email)
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        # Send email
        send_mail(
            subject="Password Reset Request",
            message=f"Use the following link to reset your password: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return True
