from django.contrib import admin

from .models import Post, Category, Location, Comment

admin.site.empty_value_display = 'Не задано'


class CommentsInline(admin.TabularInline):
    """Отображение списка комментариев."""

    fields = ('text', 'created_at', 'author')
    readonly_fields = ('created_at',)
    model = Comment

class PostInline(admin.TabularInline):
    """Отображение списка постов."""

    fields = (
        'author',
        'pub_date',
        'title',
        'text',
        'location',
        'category',
        'is_published',
    )

    model = Post
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Отображение категорий в админке."""

    list_select_related = ('author', 'location', 'category')
    inlines = (CommentsInline,)
    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        qs = qs.only(
            'author__first_name',
            'author__last_name',
            'pub_date',
            'created_at',
            'title',
            'text',
            'location__name',
            'category__title',
            'is_published',
        )
        return qs

    list_display = (
        'id',
        'title',
        'author',
        'category',
        'location',
        'pub_date',
        'created_at',
        'text',
        'is_published',
    )
    list_editable = (
        'category',
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('category', 'author', 'pub_date')
    list_display_links = ('title',)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Отображение категорий в админке"""

    inlines = (PostInline,)
    list_display = (
        'title',
        'description',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Отображение локаций в админке"""

    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Отображение комментариев в админке"""

    list_display = ('text', 'created_at', 'post')
    readonly_fields = ('created_at', 'author', 'post')
