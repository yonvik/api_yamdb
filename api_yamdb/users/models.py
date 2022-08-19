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
    username = models.CharField(db_index=True, max_length=255, unique=True)
    email = models.EmailField(db_index=True, unique=True)

    first_name = models.CharField(max_length=256, blank=True, null=True)
    last_name = models.CharField(max_length=256, blank=True, null=True)

    secret_key = models.CharField(max_length=256,
                                  db_index=True, unique=True, null=True)

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    bio = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=20,
        default=DEFAULT_USER_ROLE,
        choices=ROLE_CHOICES
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        return self.get_tokens_for_user()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def get_tokens_for_user(self):
        refresh = RefreshToken.for_user(self)
        return str(refresh.access_token)

    class Meta:
        ordering = ['pk']
