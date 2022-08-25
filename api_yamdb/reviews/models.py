from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_review_score, validate_year_title

USER_ROLE = 'user'
MODERATOR_ROLE = 'moderator'
ADMIN_ROLE = 'admin'

ROLE_CHOICES = (
    (USER_ROLE, 'Пользователь'),
    (MODERATOR_ROLE, 'Модератор '),
    (ADMIN_ROLE, 'Администратор')
)

MAX_LENGTH_USERNAME = 255
MAX_LENGTH_CONFIRMATION_CODE = 256


def get_max_length_role(roles):
    max_length = len(roles[1][0])
    for i in range(1, len(roles)):
        role_len = len(roles[i][0])
        if role_len > max_length:
            max_length = role_len
    return max_length


class User(AbstractUser):
    confirmation_code = models.CharField(
        max_length=MAX_LENGTH_CONFIRMATION_CODE,
        db_index=True,
        unique=True,
        null=True
    )
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=get_max_length_role(ROLE_CHOICES),
        default=USER_ROLE,
        choices=ROLE_CHOICES
    )
    email = models.EmailField(unique=True)

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
    score = models.IntegerField(validators=[validate_review_score])
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
        related_name='comments'
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
        validators=[validate_year_title],
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
