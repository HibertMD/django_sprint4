from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверка авторства."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class UserRedirectMixin:
    """Редирект пользователя после создания или редактирования профиля."""

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(
            'users:profile', kwargs={'username': self.object.username}
        )


class UserProfileMixin:
    """Миксин для профиля пользователя."""

    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
