import csv
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import WishlistItem


class WishlistView(LoginRequiredMixin, View):
    """
    GET  /wishlist/        — retrieve all items
    POST /wishlist/        — add a book   (body: title, author, isbn, cover_url, open_library_key)
    DELETE /wishlist/<id>/ — remove a book
    """

    def get(self, request):
        items = WishlistItem.objects.filter(user=request.user).values(
            'id', 'title', 'author', 'isbn', 'cover_url', 'added_at'
        )
        return JsonResponse({'items': list(items)})

    def post(self, request):
        import json
        data = json.loads(request.body)
        isbn = data.get('isbn', '').strip()

        # Duplicate guard
        if isbn and WishlistItem.objects.filter(user=request.user, isbn=isbn).exists():
            return JsonResponse({'message': 'Already in your wishlist.'}, status=200)

        item = WishlistItem.objects.create(
            user             = request.user,
            title            = data.get('title', ''),
            author           = data.get('author', ''),
            isbn             = isbn,
            cover_url        = data.get('cover_url', ''),
            open_library_key = data.get('open_library_key', ''),
        )
        return JsonResponse({'message': 'Added to wishlist.', 'id': item.id}, status=201)

    def delete(self, request, item_id):
        deleted, _ = WishlistItem.objects.filter(user=request.user, id=item_id).delete()
        if deleted:
            return JsonResponse({'message': 'Removed from wishlist.'})
        return JsonResponse({'error': 'Item not found.'}, status=404)


class WishlistExportView(LoginRequiredMixin, View):
    """
    GET /wishlist/export/  — download wishlist as CSV
    """
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="frugal_wishlist.csv"'

        writer = csv.writer(response)
        writer.writerow(['Title', 'Author', 'ISBN', 'Added'])
        for item in WishlistItem.objects.filter(user=request.user):
            writer.writerow([item.title, item.author, item.isbn,
                             item.added_at.strftime('%Y-%m-%d')])
        return response
