import re

from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

MINIMAL_SCORE = 1
MAXIMUM_SCORE = 10
NOT_ALLOWED_USERNAMES = ['me']


def username_validator(value: str):
    if value in NOT_ALLOWED_USERNAMES:
        raise ValidationError(
            'Поле username не может содержать значение: ', value
        )
    if re.search(r'^[\w.@+-]+\Z', value) is None:
        raise ValidationError(
            'username может состоять только из букв, '
            'цифр и спецсимволов: @.+-_')


def validate_year_title(value):
    year = timezone.datetime.now().year
    if value > timezone.datetime.now().year:
        raise serializers.ValidationError(
            f'Год выпуска не может быть больше {year}'
        )
    return value
