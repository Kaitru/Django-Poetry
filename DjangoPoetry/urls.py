"""
URL configuration for DjangoPoetry project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from poetry import views
from poetry.api import top_authors_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('poems/', views.poem_list, name='poem_list'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('become-author/', views.become_author, name='become_author'),
    path('request-critic/', views.request_critic_role, name='request_critic'),
    path('new-poem/', views.new_poem, name='new_poem'),
    path('poem/<int:poem_id>/', views.poem_detail, name='poem_detail'),
    path('poem/<int:poem_id>/rate/', views.rate_poem, name='rate_poem'),
    path('poem/<int:poem_id>/comment/', views.add_comment, name='add_comment'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('search/', views.search, name='search'),
    path('api/top-authors/', top_authors_api, name='top_authors_api'),
    path('authors/', views.authors_list, name='authors'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
