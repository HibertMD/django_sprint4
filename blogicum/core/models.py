from django.db import models


class PublishedModel(models.Model):
    """Абстрактая модель добавляющая информацию о публикации."""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_created=True,
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True
