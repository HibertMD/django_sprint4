from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].initial = timezone.localtime(
            timezone.now()
        ).strftime('%Y-%m-%dT%H:%M')
    class Meta:
        model = Post
        exclude = ('is_published', 'author')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'},)
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

