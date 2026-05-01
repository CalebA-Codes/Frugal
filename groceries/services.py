"""
Kroger API wrapper.
Auth: OAuth 2.0 Client Credentials flow — tokens expire in 30 min.
Docs: https://developer.kroger.com/documentation/

Set in .env:
    KROGER_CLIENT_ID=...
    KROGER_CLIENT_SECRET=...
"""
import base64
import time
import requests
from django.conf import settings

_token_cache: dict = {}   # simple in-memory cache; use Redis in production


def _get_token() -> str:
    """Returns a valid bearer token, refreshing if expired."""
    now = time.time()
    if _token_cache.get('expires_at', 0) > now + 60:
        return _token_cache['access_token']

    credentials = f"{settings.KROGER_CLIENT_ID}:{settings.KROGER_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    resp = requests.post(
        f"{settings.KROGER_BASE_URL}/connect/oauth2/token",
        headers={
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={'grant_type': 'client_credentials', 'scope': 'product.compact'},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    _token_cache['access_token'] = data['access_token']
    _token_cache['expires_at']   = now + data.get('expires_in', 1800)
    return _token_cache['access_token']


def search_products(query: str, location_id: str = None, limit: int = 20) -> list[dict]:
    """
    Search Kroger products by keyword.
    location_id: Kroger store location ID (optional — prices vary by store).
    """
    token = _get_token()
    params = {
        'filter.term':  query,
        'filter.limit': limit,
    }
    if location_id:
        params['filter.locationId'] = location_id

    resp = requests.get(
        f"{settings.KROGER_BASE_URL}/products",
        headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    items = resp.json().get('data', [])

    results = []
    for item in items:
        price_info = {}
        if item.get('items'):
            first = item['items'][0]
            price_info = {
                'regular_price': first.get('price', {}).get('regular'),
                'promo_price':   first.get('price', {}).get('promo'),
                'size':          first.get('size'),
                'sold_by':       first.get('soldBy'),
            }
        results.append({
            'product_id':   item.get('productId'),
            'name':         item.get('description'),
            'brand':        item.get('brand'),
            'category':     item.get('categories', [''])[0] if item.get('categories') else '',
            'department':   item.get('aisleLocations', [{}])[0].get('description', ''),
            'image_url':    (item.get('images') or [{}])[0].get('sizes', [{}])[-1].get('url'),
            **price_info,
        })
    return results


def find_nearby_stores(lat: float, lng: float, radius_miles: int = 10) -> list[dict]:
    """
    Returns Kroger store locations near a lat/lng coordinate.
    Used to get a location_id for price lookups.
    """
    token = _get_token()
    resp = requests.get(
        f"{settings.KROGER_BASE_URL}/locations",
        headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
        params={
            'filter.latLong.near': f'{lat},{lng}',
            'filter.radiusInMiles': radius_miles,
            'filter.limit': 5,
        },
        timeout=10,
    )
    resp.raise_for_status()
    stores = resp.json().get('data', [])

    return [{
        'location_id': s.get('locationId'),
        'name':        s.get('name'),
        'address':     s.get('address', {}).get('addressLine1'),
        'city':        s.get('address', {}).get('city'),
        'distance':    s.get('geolocation', {}).get('distanceInMiles'),
    } for s in stores]
