import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import SaleListing


class ListingListView(View):
    """
    GET  /marketplace/          — browse all active listings
    POST /marketplace/          — create a new listing (auth required)
    """
    def get(self, request):
        category  = request.GET.get('category')
        condition = request.GET.get('condition')
        qs = SaleListing.objects.filter(status='active')

        if category:
            qs = qs.filter(category=category)
        if condition:
            qs = qs.filter(condition=condition)

        listings = list(qs.values(
            'id', 'title', 'author', 'isbn', 'edition',
            'price', 'condition', 'category', 'status',
            'seller__username', 'created_at',
        ))
        return JsonResponse({'listings': listings, 'count': len(listings)})

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required.'}, status=401)

        data = json.loads(request.body)
        listing = SaleListing.objects.create(
            seller      = request.user,
            category    = data.get('category', 'textbook'),
            title       = data['title'],
            description = data.get('description', ''),
            price       = data['price'],
            condition   = data.get('condition', 'good'),
            isbn        = data.get('isbn', ''),
            author      = data.get('author', ''),
            edition     = data.get('edition', ''),
        )
        return JsonResponse({'message': 'Listing created.', 'id': listing.id}, status=201)


class ListingDetailView(LoginRequiredMixin, View):
    """
    PATCH  /marketplace/<id>/        — update listing (owner only)
    DELETE /marketplace/<id>/        — delete listing (owner only)
    POST   /marketplace/<id>/sold/   — mark as sold (owner only)
    """
    def _get_own_listing(self, request, listing_id):
        try:
            return SaleListing.objects.get(id=listing_id, seller=request.user)
        except SaleListing.DoesNotExist:
            return None

    def patch(self, request, listing_id):
        listing = self._get_own_listing(request, listing_id)
        if not listing:
            return JsonResponse({'error': 'Listing not found or not yours.'}, status=404)

        data = json.loads(request.body)
        for field in ('title', 'description', 'price', 'condition'):
            if field in data:
                setattr(listing, field, data[field])
        listing.save()
        return JsonResponse({'message': 'Listing updated.'})

    def delete(self, request, listing_id):
        listing = self._get_own_listing(request, listing_id)
        if not listing:
            return JsonResponse({'error': 'Listing not found or not yours.'}, status=404)
        listing.delete()
        return JsonResponse({'message': 'Listing deleted.'})


class MarkSoldView(LoginRequiredMixin, View):
    """POST /marketplace/<id>/sold/"""
    def post(self, request, listing_id):
        try:
            listing = SaleListing.objects.get(id=listing_id, seller=request.user)
        except SaleListing.DoesNotExist:
            return JsonResponse({'error': 'Listing not found or not yours.'}, status=404)

        listing.status = 'sold'
        listing.save()
        return JsonResponse({'message': 'Marked as sold.'})
