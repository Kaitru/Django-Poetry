from django.http import JsonResponse
from .views import get_top_authors

def top_authors_api(request):
    period = request.GET.get('period', 'week')
    authors = get_top_authors(period)
    data = [{
        'id': author.id,
        'username': author.username,
        'rating': float(author.user_rating),
        'url': f'/author/{author.id}/'
    } for author in authors]
    return JsonResponse({'authors': data}) 