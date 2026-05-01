# books/urls.py
from django.urls import path
from .views import SearchBooksView

urlpatterns = [
    path('search/', SearchBooksView.as_view(), name='book-search'),
]
