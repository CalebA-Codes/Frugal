from django.http import JsonResponse
from django.views import View
from .places_service import find_clothing_stores


class NearbyClothingStoresView(View):
    """
    GET /clothing/stores/?lat=40.5&lng=-88.9&radius=5000
    Front end sends coords from browser Geolocation API.
    """
    def get(self, request):
        try:
            lat    = float(request.GET['lat'])
            lng    = float(request.GET['lng'])
            radius = int(request.GET.get('radius', 5000))
        except (KeyError, ValueError):
            return JsonResponse(
                {'error': 'lat and lng are required. radius is optional (meters, default 5000).'},
                status=400,
            )

        try:
            stores = find_clothing_stores(lat, lng, radius_meters=radius)
            return JsonResponse({'stores': stores, 'count': len(stores)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=502)
