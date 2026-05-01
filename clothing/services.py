"""
Uses Google Places API (Nearby Search) to find clothing stores near a location.
Docs: https://developers.google.com/maps/documentation/places/web-service/nearby-search

Requires GOOGLE_API_KEY in .env with Places API enabled.
"""
import requests
from django.conf import settings

PLACES_NEARBY_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
PLACES_DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'


def find_clothing_stores(lat: float, lng: float, radius_meters: int = 5000) -> list[dict]:
    """
    Returns clothing stores within radius_meters of (lat, lng).
    radius_meters default = 5km (~3 miles).
    """
    resp = requests.get(
        PLACES_NEARBY_URL,
        params={
            'location':  f'{lat},{lng}',
            'radius':    radius_meters,
            'type':      'clothing_store',
            'key':       settings.GOOGLE_API_KEY,
        },
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get('results', [])

    stores = []
    for place in results:
        stores.append({
            'place_id':    place.get('place_id'),
            'name':        place.get('name'),
            'address':     place.get('vicinity'),
            'rating':      place.get('rating'),
            'open_now':    place.get('opening_hours', {}).get('open_now'),
            'lat':         place['geometry']['location']['lat'],
            'lng':         place['geometry']['location']['lng'],
            'types':       place.get('types', []),
            'maps_url':    f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}",
        })
    return stores
