"""
Wraps the Open Library API — no API key required.
Docs: https://openlibrary.org/developers/api
"""
import requests
from django.conf import settings

BASE = getattr(settings, 'OPEN_LIBRARY_BASE_URL', 'https://openlibrary.org')


def _search(params: dict) -> list[dict]:
    """
    Calls /search.json and returns a normalised list of book dicts.
    params examples:
        {'title': 'calculus'}
        {'author': 'stewart'}
        {'isbn': '9780134438986'}
        {'q': 'organic chemistry'}
    """
    try:
        resp = requests.get(f'{BASE}/search.json', params={**params, 'limit': 20}, timeout=8)
        resp.raise_for_status()
        docs = resp.json().get('docs', [])
    except requests.RequestException:
        return []

    results = []
    for doc in docs:
        results.append({
            'title':      doc.get('title', 'Unknown'),
            'author':     ', '.join(doc.get('author_name', ['Unknown'])),
            'isbn':       (doc.get('isbn') or [''])[0],
            'year':       doc.get('first_publish_year'),
            'edition':    doc.get('edition_count'),
            'cover_url':  f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                          if doc.get('cover_i') else None,
            'open_library_key': doc.get('key'),   # e.g. /works/OL12345W
        })
    return results


def search_by_title(title: str) -> list[dict]:
    return _search({'title': title})


def search_by_author(author: str) -> list[dict]:
    return _search({'author': author})


def search_by_isbn(isbn: str) -> list[dict]:
    # ISBN search uses 'q' with the raw ISBN
    return _search({'isbn': isbn})


def get_book_detail(open_library_key: str) -> dict:
    """
    Fetches full work detail from /works/<key>.json
    open_library_key example: '/works/OL12345W'
    """
    try:
        resp = requests.get(f'{BASE}{open_library_key}.json', timeout=8)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return {}
