from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView

from .forms import PostForm
from .models import Post, Category
from .constants import POSTS_PER_PAGE
from users.views import UserProfileMixin

User = get_user_model()


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            return Post.objects.filter(category__slug=category_slug)
        return Post.objects.all()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(
            'users:profile', kwargs={'username': self.object.author}
        )


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.object.id}
        )


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')


class CategoryPostsListView(ListView):
    model = Category
    slug_url_kwarg = "category_slug"
    slug_field = "category_slug"
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE


