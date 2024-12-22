from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from user.manager import UserManager


class User(AbstractUser):
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    profile_image = models.ImageField(upload_to='images/profile_images/%Y/%m', blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=["first_name", "last_name", "username", "email", "phone"]),
        ]
