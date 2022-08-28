import datetime as dt
import re

from django.core.exceptions import ValidationError
from django.conf import settings

NOT_ALLOWED_USERNAMES = ['me']


def username_validator(value: str):
    if value in NOT_ALLOWED_USERNAMES:
        raise ValidationError(
            'Поле username не может содержать значение: ', value
        )
    if re.search(r'^[\w.@+-]+\Z', value) is None:
        raise ValidationError(
            'username может состоять только из букв, '
            f'цифр и спецсимволов: {settings.USERNAME_SPECIAL_CHARACTER}'
            'недопустимые значения: ()*&^%$#!=~`?')
    return value


def validate_year_title(value):
    year = dt.date.today().year
    if value > year:
        raise ValidationError(
            f'Проверьте год ({year}), он не должен быть больше текущего')
    return value
