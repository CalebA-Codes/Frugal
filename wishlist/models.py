from django.db import models
from django.conf import settings


class WishlistItem(models.Model):
    """Stores a book a user wants to track/buy."""
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist'
    )
    # We store enough info so we don't need a round-trip to Open Library every time
    title      = models.CharField(max_length=512)
    author     = models.CharField(max_length=512, blank=True)
    isbn       = models.CharField(max_length=20, blank=True)
    cover_url  = models.URLField(blank=True)
    open_library_key = models.CharField(max_length=64, blank=True)
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'isbn')   # prevents duplicates per user
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} — {self.title}"
