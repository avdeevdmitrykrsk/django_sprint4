from core.models import PublishedCreatedModel

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(PublishedCreatedModel):
    title = models.CharField('Заголовок', max_length=256)
    description: str = models.TextField('Описание')
    slug: str = models.SlugField(
        'Идентификатор', unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedCreatedModel):
    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedCreatedModel):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User, verbose_name=('Автор публикации'), on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, verbose_name=('Местоположение'),
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    category = models.ForeignKey(
        Category, verbose_name=('Категория'),
        on_delete=models.SET_NULL,
        null=True, blank=False
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title
