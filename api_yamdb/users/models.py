from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.db import models

from random import randint

from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import RECIPIENTS_EMAIL

ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор '),
    ('admin', 'Администратор')
)

DEFAULT_USER_ROLE = ROLE_CHOICES[0][0]
SUPERUSER_ROLE = ROLE_CHOICES[2][0]


class UserManager(BaseUserManager):
    """
    Django требует, чтобы кастомные пользователи определяли свой собственный
    класс Manager. Унаследовавшись от BaseUserManager, мы получаем много того
    же самого кода, который Django использовал для создания User (для демонстрации).
    """

    def create_user(self, **kwargs):
        """ Создает и возвращает пользователя с имэйлом и именем. """
        if kwargs.get('username') is None:
            raise TypeError('Users must have a username.')

        if kwargs.get('email') is None:
            raise TypeError('Users must have an email address.')

        random = randint(100000, 1000000)
        kwargs['secret_key'] = random
        user = self.model(**kwargs)
        user.save()
        send_mail(
            'Регистрация нового пользователя',
            'Это ваш token для получения JWTТокена:' f'{random}',
            RECIPIENTS_EMAIL,
            [user.email],
        )
        return user

    def create_superuser(self, **kwargs):
        """ Создает и возввращет пользователя с привилегиями суперадмина. """
        if kwargs.get('password') is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.role = SUPERUSER_ROLE
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Каждому пользователю нужен понятный человеку уникальный идентификатор,
    # который мы можем использовать для предоставления User в пользовательском
    # интерфейсе. Мы так же проиндексируем этот столбец в базе данных для
    # повышения скорости поиска в дальнейшем.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # Так же мы нуждаемся в поле, с помощью которого будем иметь возможность
    # связаться с пользователем и идентифицировать его при входе в систему.
    # Поскольку адрес почты нам нужен в любом случае, мы также будем
    # использовать его для входы в систему, так как это наиболее
    # распространенная форма учетных данных на данный момент (ну еще телефон).
    email = models.EmailField(db_index=True, unique=True)

    # Случайно сгенерированный ключ для подтверждения по почте JWTToken
    secret_key = models.IntegerField(db_index=True, unique=True, null=True)

    # Когда пользователь более не желает пользоваться нашей системой, он может
    # захотеть удалить свой аккаунт. Для нас это проблема, так как собираемые
    # нами данные очень ценны, и мы не хотим их удалять :) Мы просто предложим
    # пользователям способ деактивировать учетку вместо ее полного удаления.
    # Таким образом, они не будут отображаться на сайте, но мы все еще сможем
    # далее анализировать информацию.
    is_active = models.BooleanField(default=True)

    # Этот флаг определяет, кто может войти в административную часть нашего
    # сайта. Для большинства пользователей это флаг будет ложным.
    is_staff = models.BooleanField(default=False)

    # Временная метка создания объекта.
    created_at = models.DateTimeField(auto_now_add=True)

    # Временная метка показывающая время последнего обновления объекта.
    updated_at = models.DateTimeField(auto_now=True)

    # Дополнительный поля, необходимые Django
    # при указании кастомной модели пользователя.

    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=20,
        default=DEFAULT_USER_ROLE,
        choices=ROLE_CHOICES
    )

    # Свойство USERNAME_FIELD сообщает нам, какое поле мы будем использовать
    # для входа в систему. В данном случае мы хотим использовать почту.
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    # Сообщает Django, что определенный выше класс UserManager
    # должен управлять объектами этого типа.
    objects = UserManager()

    def __str__(self):
        """ Строковое представление модели (отображается в консоли) """
        return self.email

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self.get_tokens_for_user()

    def get_full_name(self):
        """
        Этот метод требуется Django для таких вещей, как обработка электронной
        почты. Обычно это имя фамилия пользователя, но поскольку мы не
        используем их, будем возвращать username.
        """
        return self.username

    def get_short_name(self):
        """ Аналогично методу get_full_name(). """
        return self.username

    def get_tokens_for_user(self):
        refresh = RefreshToken.for_user(self)
        return str(refresh.access_token)
