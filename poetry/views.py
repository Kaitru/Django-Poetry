from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, Poem, Genre, Mood, Comment, CriticComment, UserRating, CriticRating
from .forms import UserRegistrationForm, AuthorRegistrationForm, PoemForm, CommentForm, CriticCommentForm, ProfileEditForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models

def home(request):
    poem_list = Poem.objects.select_related('author', 'mood').prefetch_related('genres').order_by('-created_at')
    
    # Создаем пагинатор, 20 стихов на страницу
    paginator = Paginator(poem_list, 20)
    page = request.GET.get('page')
    
    try:
        poems = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу
        poems = paginator.page(1)
    except EmptyPage:
        # Если страница больше максимальной, возвращаем последнюю
        poems = paginator.page(paginator.num_pages)
    
    top_authors = get_top_authors()
    return render(request, 'poetry/home.html', {
        'poems': poems,
        'top_authors': top_authors
    })

def get_top_authors(period='week'):
    now = timezone.now()
    if period == 'day':
        start_date = now - timedelta(days=1)
    elif period == 'week':
        start_date = now - timedelta(weeks=1)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'three_months':
        start_date = now - timedelta(days=90)
    elif period == 'six_months':
        start_date = now - timedelta(days=180)
    elif period == 'year':
        start_date = now - timedelta(days=365)
    else:
        start_date = None
    
    authors = CustomUser.objects.filter(role='author')
    if start_date:
        authors = authors.filter(poems__created_at__gte=start_date)
    
    return authors.annotate(
        avg_rating=Avg('poems__user_rating'),
        poem_count=Count('poems')
    ).order_by('-avg_rating', '-poem_count')[:5]

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    
    return render(request, 'poetry/login.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Автоматически входим после регистрации
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'poetry/register.html', {'form': form})

@login_required
def become_author(request):
    if request.method == 'POST':
        form = AuthorRegistrationForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'author'
            user.save()
            messages.success(request, 'Теперь вы автор!')
            return redirect('profile')
    else:
        form = AuthorRegistrationForm(instance=request.user)
    return render(request, 'poetry/become_author.html', {'form': form})

@login_required
def request_critic_role(request):
    if request.method == 'POST':
        request.user.critic_requested = True
        request.user.save()
        messages.info(request, 'Заявка на роль критика отправлена администрации')
        return redirect('profile')
    return render(request, 'poetry/request_critic.html')

@login_required
def new_poem(request):
    if request.user.role != 'author':
        messages.error(request, 'Только авторы могут создавать стихи')
        return redirect('home')
        
    if request.method == 'POST':
        form = PoemForm(request.POST)
        if form.is_valid():
            poem = form.save(commit=False)
            poem.author = request.user
            poem.save()
            form.save_m2m()  # Сохраняем many-to-many отношения
            messages.success(request, 'Стихотворение успешно создано!')
            return redirect('poem_detail', poem_id=poem.id)
    else:
        form = PoemForm()
    
    return render(request, 'poetry/new_poem.html', {'form': form})

def poem_detail(request, poem_id):
    poem = get_object_or_404(Poem, pk=poem_id)
    comments = Comment.objects.filter(poem=poem, parent=None).order_by('-created_at')
    critic_comments = CriticComment.objects.filter(poem=poem).order_by('-created_at')
    
    # Получаем рейтинг текущего пользователя для этого стиха, если он авторизован
    user_rating = None
    critic_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = UserRating.objects.get(user=request.user, poem=poem)
        except UserRating.DoesNotExist:
            pass
            
        if hasattr(request.user, 'role') and request.user.role == 'critic':
            try:
                critic_rating = CriticRating.objects.get(critic=request.user, poem=poem)
            except CriticRating.DoesNotExist:
                pass
    
    return render(request, 'poetry/poem_detail.html', {
        'poem': poem,
        'comments': comments,
        'critic_comments': critic_comments,
        'comment_form': CommentForm(),
        'critic_comment_form': CriticCommentForm() if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'critic' else None,
        'user_rating': user_rating,
        'critic_rating': critic_rating
    })

@login_required
def rate_poem(request, poem_id):
    poem = get_object_or_404(Poem, pk=poem_id)
    rating = request.POST.get('rating')
    
    if not rating:
        messages.error(request, 'Необходимо указать оценку')
        return redirect('poem_detail', poem_id=poem_id)
        
    try:
        rating = int(rating)
    except ValueError:
        messages.error(request, 'Некорректная оценка')
        return redirect('poem_detail', poem_id=poem_id)
        
    if request.user.role == 'critic':
        if not (1 <= rating <= 10):
            messages.error(request, 'Оценка должна быть от 1 до 10')
            return redirect('poem_detail', poem_id=poem_id)
            
        rating_obj, created = CriticRating.objects.update_or_create(
            critic=request.user,
            poem=poem,
            defaults={'rating': rating}
        )
        
        # Обновляем средний рейтинг критиков
        avg_rating = CriticRating.objects.filter(poem=poem).aggregate(Avg('rating'))['rating__avg'] or 0
        poem.critic_rating = avg_rating
        poem.save()
        
    else:
        if not (1 <= rating <= 5):
            messages.error(request, 'Оценка должна быть от 1 до 5')
            return redirect('poem_detail', poem_id=poem_id)
            
        rating_obj, created = UserRating.objects.update_or_create(
            user=request.user,
            poem=poem,
            defaults={'rating': rating}
        )
        
        # Обновляем средний пользовательский рейтинг
        avg_rating = UserRating.objects.filter(poem=poem).aggregate(Avg('rating'))['rating__avg'] or 0
        poem.user_rating = avg_rating
        poem.save()
    
    messages.success(request, 'Оценка сохранена')
    return redirect('poem_detail', poem_id=poem_id)

@login_required
def add_comment(request, poem_id):
    poem = get_object_or_404(Poem, pk=poem_id)
    
    if request.method == 'POST':
        if request.user.role == 'critic':
            form = CriticCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.critic = request.user
                comment.poem = poem
                comment.save()
                messages.success(request, 'Комментарий добавлен')
        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.poem = poem
                comment.save()
                messages.success(request, 'Комментарий добавлен')
    
    return redirect('poem_detail', poem_id=poem_id)

def author_detail(request, author_id):
    author = get_object_or_404(CustomUser, id=author_id, role='author')
    sort_by = request.GET.get('sort', 'new')
    
    if sort_by == 'popular':
        poems = author.poems.order_by('-user_rating')
    else:
        poems = author.poems.order_by('-created_at')
    
    top_genres = Genre.objects.filter(poem__author=author).annotate(
        count=Count('poem')
    ).order_by('-count')[:5]
    
    return render(request, 'poetry/author_detail.html', {
        'author': author,
        'poems': poems,
        'top_genres': top_genres,
        'sort_by': sort_by
    })

def search(request):
    query = request.GET.get('q', '')
    genre = request.GET.get('genre')
    mood = request.GET.get('mood')
    
    poems = Poem.objects.select_related('author', 'mood').prefetch_related('genres').all()
    
    if query:
        poems = poems.filter(
            models.Q(title__icontains=query) |
            models.Q(content__icontains=query) |
            models.Q(author__first_name__icontains=query) |
            models.Q(author__last_name__icontains=query)
        )
    
    if genre:
        poems = poems.filter(genres__id=genre)
    if mood:
        poems = poems.filter(mood__id=mood)
    
    # Добавляем пагинацию для результатов поиска
    paginator = Paginator(poems.distinct(), 20)  # distinct() чтобы избежать дубликатов
    page = request.GET.get('page')
    
    try:
        poems = paginator.page(page)
    except PageNotAnInteger:
        poems = paginator.page(1)
    except EmptyPage:
        poems = paginator.page(paginator.num_pages)
    
    return render(request, 'poetry/search.html', {
        'poems': poems,
        'query': query,
        'genres': Genre.objects.all(),
        'moods': Mood.objects.all(),
        'selected_genre': genre,
        'selected_mood': mood
    })

@login_required
def profile(request):
    if request.method == 'POST':
        if 'profile_edit' in request.POST:
            profile_form = ProfileEditForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профиль успешно обновлен')
                return redirect('profile')
        elif 'avatar' in request.FILES:
            request.user.avatar = request.FILES['avatar']
            request.user.save()
            messages.success(request, 'Аватар обновлен')
        elif action := request.POST.get('action'):
            if action == 'become_author':
                return redirect('become_author')
            elif action == 'request_critic':
                return redirect('request_critic')
    else:
        profile_form = ProfileEditForm(instance=request.user)
    
    user_poems = []
    if request.user.role == 'author':
        user_poems = request.user.poems.all()
    
    user_comments = Comment.objects.filter(user=request.user)
    user_ratings = UserRating.objects.filter(user=request.user)
    
    return render(request, 'poetry/profile.html', {
        'profile_form': profile_form,
        'user_poems': user_poems,
        'user_comments': user_comments,
        'user_ratings': user_ratings
    })

def poem_list(request):
    poem_list = Poem.objects.select_related('author', 'mood').prefetch_related('genres').order_by('-created_at')
    
    paginator = Paginator(poem_list, 20)
    page = request.GET.get('page')
    
    try:
        poems = paginator.page(page)
    except PageNotAnInteger:
        poems = paginator.page(1)
    except EmptyPage:
        poems = paginator.page(paginator.num_pages)
    
    return render(request, 'poetry/poem_list.html', {
        'poems': poems
    })

def authors_list(request):
    authors = CustomUser.objects.filter(role='author').annotate(
        avg_rating=Avg('poems__user_rating'),
        poem_count=Count('poems')
    ).order_by('-avg_rating')
    
    paginator = Paginator(authors, 20)
    page = request.GET.get('page')
    
    try:
        authors = paginator.page(page)
    except PageNotAnInteger:
        authors = paginator.page(1)
    except EmptyPage:
        authors = paginator.page(paginator.num_pages)
    
    return render(request, 'poetry/authors_list.html', {
        'authors': authors
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home') 