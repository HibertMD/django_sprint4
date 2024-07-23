from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView

from .forms import ProfileForm
from blog.constants import POSTS_PER_PAGE

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object == self.request.user
    
    
class UserRedirectMixin:
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(
            'users:profile', kwargs={'username': self.object.username}
        )


class UserProfileMixin:
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'


class UserCreateView(UserRedirectMixin, CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm


class UserProfileView(UserProfileMixin, ListView):
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['profile'] = user
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        queryset = user.posts.all().annotate(comment_count=Count('comments')
        ).order_by('-pub_date')
        return queryset


class UserProfileUpdate(LoginRequiredMixin, OnlyAuthorMixin, UserProfileMixin,
                        UserRedirectMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = ProfileForm
