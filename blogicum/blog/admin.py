from django.contrib import admin

from .models import Post, Category, Location

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.TabularInline):
    """Отображение списка постов для редактирования"""

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
    """
    Отображение категорий в админке

    Попытался получить все посты для админки за один запрос к БД.
    Но так и не получилось для поля 'category' в list_editable
    тянется отдельный запрос для каждого поста.
    """

    list_select_related = ('author', 'location', 'category',)

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

    inlines = (
        PostInline,
    )
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
