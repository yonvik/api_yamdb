from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from . import validators

USER_ROLE = 'user'
MODERATOR_ROLE = 'moderator'
ADMIN_ROLE = 'admin'

ROLE_CHOICES = (
    (USER_ROLE, 'Пользователь'),
    (MODERATOR_ROLE, 'Модератор'),
    (ADMIN_ROLE, 'Администратор')
)

MAX_LENGTH_USERNAME = 255
MAX_LENGTH_CONFIRMATION_CODE = 256
MAX_LENGTH_EMAIL = 255

MINIMAL_SCORE = 1
MAXIMUM_SCORE = 10


class User(AbstractUser):
    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        help_text=(f'Required. {MAX_LENGTH_USERNAME} characters or fewer. '
                   'Letters, digits and @/./+/-/_ only.'),
        validators=[validators.username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    confirmation_code = models.CharField(
        max_length=MAX_LENGTH_CONFIRMATION_CODE,
        unique=True,
        null=True
    )
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=len(max([choice[0] for choice in ROLE_CHOICES], key=len)),
        default=USER_ROLE,
        choices=ROLE_CHOICES
    )
    email = models.EmailField(max_length=MAX_LENGTH_EMAIL, unique=True)

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN_ROLE

    @property
    def is_moderator(self):
        return self.role == MODERATOR_ROLE

    class Meta:
        ordering = ['username']


class PubDateModel(models.Model):
    """Абстрактная модель. Добавляет дату публикации."""
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class BaseReviewComment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        ordering = ['text']


class Review(BaseReviewComment, PubDateModel):
    score = models.IntegerField(validators=[
        MaxValueValidator(
            limit_value=MAXIMUM_SCORE,
            message=f'Оценка не может быть больше {MAXIMUM_SCORE}'),
        MinValueValidator(
            limit_value=MINIMAL_SCORE,
            message=f'Оценка не может быть меньше {MINIMAL_SCORE}'
        )
    ])
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE
    )

    class Meta(BaseReviewComment.Meta):
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]


class Comment(BaseReviewComment, PubDateModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
    )

    class Meta(BaseReviewComment.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'


class BaseGenreCategory(models.Model):
    slug = models.SlugField('Слаг', unique=True, max_length=50)
    name = models.CharField('Название', max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('name',)


class Category(BaseGenreCategory):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseGenreCategory):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField('Название', max_length=200)
    year = models.IntegerField(
        validators=[validators.validate_year_title],
        verbose_name='Дата выпуска'
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
