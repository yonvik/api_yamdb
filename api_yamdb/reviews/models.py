from datetime import datetime

from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth import get_user_model

from .validators import validate_review_score
from core.models import PubDateModel

User = get_user_model()


class Review(PubDateModel):
    text = models.TextField()
    score = models.IntegerField(validators=[validate_review_score])
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta:
        ordering = ['pk']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]


class Comment(PubDateModel):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        ordering = ['pk']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'


class Category(models.Model):
    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField('Слаг', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=256)
    slug = models.SlugField('Слаг', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField('Название', max_length=200)
    year = models.PositiveSmallIntegerField(
        'Год выпуска',
        validators=(MaxValueValidator(datetime.now().year),)
    )
    description = models.TextField('Описание', blank=True, null=True)
    genre = models.ManyToManyField(Genre, 'Жанр', blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
