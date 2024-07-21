from django import forms

from blog.models import Post
from django.contrib.auth import get_user_model

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('is_published', 'author')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'date'})
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)




