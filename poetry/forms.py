from django import forms
from .models import CustomUser, Poem, Comment, CriticComment
from django.core.validators import RegexValidator

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class AuthorRegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Номер телефона должен быть в формате: '+999999999'"
        )]
    )
    
    class Meta:
        model = CustomUser
        fields = ('phone_number',)

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError('Этот номер телефона уже зарегистрирован')
        return phone

class PoemForm(forms.ModelForm):
    class Meta:
        model = Poem
        fields = ('title', 'content', 'genres', 'mood')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class CriticCommentForm(forms.ModelForm):
    class Meta:
        model = CriticComment
        fields = ('content',)

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email'
        } 