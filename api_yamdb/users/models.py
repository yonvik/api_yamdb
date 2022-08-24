from django.contrib.auth.models import AbstractUser
from django.db import models

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
