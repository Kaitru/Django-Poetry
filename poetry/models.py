from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class CustomUser(AbstractUser):
    READER = 'reader'
    AUTHOR = 'author'
    CRITIC = 'critic'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (READER, 'Читатель'),
        (AUTHOR, 'Автор'),
        (CRITIC, 'Критик'),
        (ADMIN, 'Администратор'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=READER)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    user_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    critic_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    critic_requested = models.BooleanField(default=False)

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Mood(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Poem(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='poems')
    genres = models.ManyToManyField(Genre)
    mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    critic_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class UserRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    class Meta:
        unique_together = ['user', 'poem']

class CriticRating(models.Model):
    critic = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    
    class Meta:
        unique_together = ['critic', 'poem']

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

class CriticComment(models.Model):
    critic = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at'] 