from django.contrib import admin
from .models import CustomUser, Genre, Mood, Poem, Comment, CriticComment, UserRating, CriticRating

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'phone_number')
    list_filter = ('role',)
    search_fields = ('username', 'phone_number')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Poem)
class PoemAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'mood', 'created_at', 'user_rating', 'critic_rating')
    list_filter = ('mood', 'genres')
    search_fields = ('title', 'content', 'author__username')
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'poem', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'poem__title')

@admin.register(CriticComment)
class CriticCommentAdmin(admin.ModelAdmin):
    list_display = ('critic', 'poem', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'critic__username', 'poem__title')

@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'poem', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__username', 'poem__title')

@admin.register(CriticRating)
class CriticRatingAdmin(admin.ModelAdmin):
    list_display = ('critic', 'poem', 'rating')
    list_filter = ('rating',)
    search_fields = ('critic__username', 'poem__title') 