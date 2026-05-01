# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extends Django's built-in user with Frugal-specific fields.
    USERNAME_FIELD remains 'username'; email is also stored.
    """
    email = models.EmailField(unique=True)
    saved_money_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text="Running total of money saved via Frugal"
    )
    location_lat  = models.FloatField(null=True, blank=True)
    location_lng  = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.username
