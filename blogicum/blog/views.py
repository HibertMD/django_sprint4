from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .forms import CommentForm, PostForm
from .constants import POSTS_PER_PAGE
from .models import Category, Comment, Post


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверка авторства."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostListView(ListView):
    """Представление списка постов."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        """
        Возвращает опубликованные посты принадлежащие выбранной категории.

        Или все опубликованные посты если категория не выбрана.
        Возвращает 404 если категория снята с публикации.
        """
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = Category.objects.filter(
                slug=category_slug,
                is_published=True,
            ).first()
            if category:
                return category.posts(manager='published').all(
                ).annotate(comment_count=Count('comments')
                           ).order_by('-pub_date')
            else:
                raise Http404
        return Post.objects.published(
        ).annotate(comment_count=Count('comments')
                   ).order_by('-pub_date')


class PostDetailView(DetailView):
    """Детальное представление поста."""

    model = Post
    template_name = 'blog/detail.html'

    def get(self, request, *args, **kwargs):
        """Возвращает опубликованные посты. Или все посты автора."""
        self.object = self.get_object()
        if (all(
                [
                    self.object.is_published,
                    self.object.pub_date <= timezone.now(),
                    self.object.category.is_published
                ])
                or (
                    self.object.author == self.request.user
                )
        ):
            return super().get(request, *args, **kwargs)
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        """Добавляет в контекст форму для комментариев и сами комментарии."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        ).order_by('created_at')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Добавляет в поле автора пользователя написавшего пост."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        """Редирект при успешном создании поста."""
        return reverse_lazy(
            'users:profile', kwargs={'username': self.object.author}
        )


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Представление для редактирования поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    redirect_field_name = None

    def handle_no_permission(self):
        """Редирект пользователя без прав на редактирование."""
        post_id = self.kwargs['pk']
        return redirect('blog:post_detail', post_id)

    def get_success_url(self, *args, **kwargs):
        """Редирект пользователя после редактирования."""
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.object.id}
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Представление для удаления поста."""

    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:index')

    def get(self, request, *args, **kwargs):
        """Вызывает 404 при переходе на страницу не опубликованного поста."""
        self.object = self.get_object()
        if not self.object.is_published:
            raise Http404
        return super().get(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания комментария."""

    object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        """Получает объект связанной модели поста."""
        self.object = get_object_or_404(Post, pk=kwargs['pk'], )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Добавляет автора и связанный пост."""
        self.object = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        form.instance.post = self.object
        return super().form_valid(form)

    def get_success_url(self):
        """Редирект при успешном создании комментария."""
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.id})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    """Представление редактирования комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        """Возвращает объект комментария или 404 если такого нет."""
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return comment

    def get_success_url(self, *args, **kwargs):
        """Редирект при успешном редактировании."""
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_id']}
        )


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Представление для удаления комментария."""

    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        """Возвращает объект комментария или 404 если такого нет."""
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return comment

    def get_success_url(self, *args, **kwargs):
        """Редирект при успешном редактировании."""
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_id']}
        )

    def get_context_data(self, **kwargs):
        """Удаляет форму комментария из контекста."""
        context = super().get_context_data(**kwargs)
        context['form'] = None
        return context
