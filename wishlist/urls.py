from django.urls import path
from .views import WishlistView, WishlistExportView

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist'),
    path('<int:item_id>/', WishlistView.as_view(), name='wishlist-item'),
    path('export/', WishlistExportView.as_view(), name='wishlist-export'),
]
