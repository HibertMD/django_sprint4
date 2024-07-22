from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView

from .forms import PostForm, CommentForm
from .models import Post, Category, Comment
from .constants import POSTS_PER_PAGE


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            return Post.objects.filter(category__slug=category_slug)
        return Post.published.all()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
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


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.object.id}
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:index')


class CategoryPostsListView(ListView):
    model = Category
    slug_url_kwarg = 'category_slug'
    slug_field = 'category_slug'
    template_name = 'blog/category.html'
    paginate_by = POSTS_PER_PAGE


class CommentCreateView(LoginRequiredMixin, CreateView):
    object = None
    model = Comment
    form_class = CommentForm
    
    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs['pk'],)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        self.object = get_object_or_404(Post, pk=self.kwargs['pk'], )
        form.instance.author = self.request.user
        form.instance.post = self.object
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.id})


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return Comment.objects.get(pk=self.kwargs['comment_id'])

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_id']}
        )


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        return Comment.objects.get(pk=self.kwargs['comment_id'])
    
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_id']}
        )
