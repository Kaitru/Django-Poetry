from django.shortcuts import redirect
from django.contrib import messages

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path.startswith('/new-poem/') and request.user.role != 'author':
                messages.error(request, 'Только авторы могут создавать стихи')
                return redirect('home')
            
            if request.path.startswith('/critic-comment/') and request.user.role != 'critic':
                messages.error(request, 'Только критики могут оставлять критические комментарии')
                return redirect('home')
        
        response = self.get_response(request)
        return response 