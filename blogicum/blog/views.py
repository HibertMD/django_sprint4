from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

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
            category = Category.objects.filter(
                slug=category_slug,
                is_published=True,
                ).first()
            if category:
                return category.posts(
                    manager='published').all(
                    ).annotate(comment_count=Count('comments')
                               ).order_by('-pub_date')
            else:
                raise Http404
        return Post.objects.published(
        ).annotate(comment_count=Count('comments')
        ).order_by('-pub_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        ).order_by('created_at')
        post = context['post']
        #TODO
        if post.is_published and post.category.is_published:
            return context
        elif post.author == self.request.user:
            return context
        else:
            raise Http404


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

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
    redirect_field_name = None
    
    def handle_no_permission(self):
        post_id = self.kwargs['pk']
        print(post_id)
        return redirect('blog:post_detail', post_id)
    
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.object.id}
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:index')
    
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_published:
            raise Http404
        return super().get(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    object = None
    model = Comment
    form_class = CommentForm
    
    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs['pk'],)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        self.object = get_object_or_404(Post, pk=self.kwargs['pk'])
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
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        return comment

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = None
        return context
