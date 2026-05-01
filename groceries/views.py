from django.http import JsonResponse
from django.views import View
from .kroger_service import search_products, find_nearby_stores


class GrocerySearchView(View):
    """
    GET /groceries/search/?q=milk&location_id=optional
    """
    def get(self, request):
        query       = request.GET.get('q', '').strip()
        location_id = request.GET.get('location_id', None)

        if not query:
            return JsonResponse({'error': 'Query parameter "q" is required.'}, status=400)

        try:
            results = search_products(query, location_id=location_id)
            return JsonResponse({'results': results, 'count': len(results)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=502)


class NearbyStoresView(View):
    """
    GET /groceries/stores/?lat=40.5&lng=-88.9
    Front end passes coords from browser Geolocation API.
    """
    def get(self, request):
        try:
            lat = float(request.GET['lat'])
            lng = float(request.GET['lng'])
        except (KeyError, ValueError):
            return JsonResponse(
                {'error': 'lat and lng query params are required as floats.'}, status=400
            )

        try:
            stores = find_nearby_stores(lat, lng)
            return JsonResponse({'stores': stores})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=502)
