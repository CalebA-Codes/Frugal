from django.http import JsonResponse
from django.views import View
from .services import search_by_title, search_by_author, search_by_isbn


class SearchBooksView(View):
    """
    GET /books/search/?q=calculus&by=title|author|isbn
    """
    def get(self, request):
        query = request.GET.get('q', '').strip()
        by    = request.GET.get('by', 'title').lower()

        if not query:
            return JsonResponse({'error': 'Query parameter "q" is required.'}, status=400)

        if by == 'author':
            results = search_by_author(query)
        elif by == 'isbn':
            results = search_by_isbn(query)
        else:
            results = search_by_title(query)

        return JsonResponse({'results': results, 'count': len(results)})
