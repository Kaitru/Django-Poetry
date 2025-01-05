from django.core.management.base import BaseCommand
from poetry.models import CustomUser, Poem, Genre, Mood
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Generates test data for the poetry app'

    def handle(self, *args, **kwargs):
        # Список авторов
        authors = [
            ('Анна', 'Ахматова'),
            ('Марина', 'Цветаева'),
            ('Борис', 'Пастернак'),
            ('Владимир', 'Маяковский'),
            ('Иосиф', 'Бродский'),
            ('Белла', 'Ахмадулина'),
            ('Николай', 'Гумилев'),
            ('Осип', 'Мандельштам'),
            ('Александр', 'Блок'),
            ('Федор', 'Тютчев')
        ]
        
        # Создаем авторов
        for first_name, last_name in authors:
            username = f"{last_name.lower()}"
            user = CustomUser.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="testpass123",
                first_name=first_name,
                last_name=last_name,
                role='author'
            )
            
            # Генерируем стихи для каждого автора
            num_poems = random.randint(10, 30)
            for i in range(num_poems):
                poem = Poem.objects.create(
                    title=f"Стихотворение {i+1}",
                    content=f"Содержание стихотворения {i+1}...",
                    author=user,
                    mood=Mood.objects.order_by('?').first(),
                    user_rating=random.uniform(3.5, 5.0),
                    critic_rating=random.uniform(7.0, 10.0),
                    created_at=timezone.now()
                )
                # Добавляем случайные жанры
                genres = Genre.objects.order_by('?')[:random.randint(1, 3)]
                poem.genres.set(genres)

        self.stdout.write(self.style.SUCCESS('Successfully generated test data')) 