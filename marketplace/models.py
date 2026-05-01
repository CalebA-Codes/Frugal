from django.db import models
from django.conf import settings


class SaleListing(models.Model):
    class Category(models.TextChoices):
        TEXTBOOK = 'textbook', 'Textbook'
        CLOTHING = 'clothing', 'Clothing'

    class Condition(models.TextChoices):
        NEW       = 'new',       'New'
        LIKE_NEW  = 'like_new',  'Like New'
        GOOD      = 'good',      'Good'
        FAIR      = 'fair',      'Fair'
        POOR      = 'poor',      'Poor'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        SOLD   = 'sold',   'Sold'

    seller      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings'
    )
    category    = models.CharField(max_length=20, choices=Category.choices)
    title       = models.CharField(max_length=512)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    condition   = models.CharField(max_length=20, choices=Condition.choices)
    status      = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    # Textbook-specific fields (optional for clothing)
    isbn        = models.CharField(max_length=20, blank=True)
    author      = models.CharField(max_length=256, blank=True)
    edition     = models.CharField(max_length=64, blank=True)

    # Image upload
    image       = models.ImageField(upload_to='marketplace/', blank=True, null=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — ${self.price} ({self.status})"
