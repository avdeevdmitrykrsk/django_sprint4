from django.db import models


class PublishedCreatedModel(models.Model):
    """Абстрактная модель. Добвляет флаг is_published и дату создания."""

    is_published = models.BooleanField(
        'Опубликовано', default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено', auto_now=False, auto_now_add=True
    )

    class Meta:
        abstract = True
