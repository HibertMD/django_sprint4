"""Модели для блога"""
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.db import models


from .constants import CHAR_FIELD_MAX_LEN
from core.models import PublishedModel


class PostQuerySet(models.QuerySet):
    """Расширяет стандартный QuerySet."""

    def with_related_data(self):
        """Подгружает все связанные поля."""
        return self.select_related(
            'location',
            'category',
            'author'
        )

    def published(self):
        """Фильтрует посты"""
        return self.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )


class PublishedPostManager(models.Manager):
    """Возвращает связанные и отфильтрованные поля"""

    def get_queryset(self):
        return (
            PostQuerySet(self.model)
            .with_related_data()
            .published()
        )


class User(get_user_model()):

    class Meta:
        proxy = True

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Category(PublishedModel):
    """Модель категории поста."""

    title = models.CharField(
        max_length=CHAR_FIELD_MAX_LEN,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'
        )
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)


class Location(PublishedModel):
    """Модель локации поста."""

    name = models.CharField(
        max_length=CHAR_FIELD_MAX_LEN,
        verbose_name='Название места',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)


class Post(PublishedModel):
    """Модель поста."""

    title = models.CharField(
        max_length=CHAR_FIELD_MAX_LEN,
        verbose_name='Заголовок',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Добавить изображение', upload_to='birthdays_images', blank=True
    )

    objects = PostQuerySet.as_manager()
    published = PublishedPostManager()

    def __str__(self):
        return self.title

    class Meta:
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def get_absolute_url(self):
        return reverse('post:post_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ('-created_at',)
