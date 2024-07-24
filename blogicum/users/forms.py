from django import forms

from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileForm(forms.ModelForm):
    """Форма профиля пользователя"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)
