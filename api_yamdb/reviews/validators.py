import datetime as dt
import re

from django.core.exceptions import ValidationError

NOT_ALLOWED_USERNAMES = ['me']


def username_validator(value: str):
    if value in NOT_ALLOWED_USERNAMES:
        raise ValidationError(
            'Поле username не может содержать значение: ', value
        )
    if re.search(r'^[\w.@+-]+\Z', value) is None:
        not_allowed_characters = ' '.join(re.findall(r'[^\w.@+-]+', value))
        raise ValidationError(
            f'username недопустимое значение: {not_allowed_characters}')
    return value


def validate_year_title(value):
    year = dt.date.today().year
    if value > year:
        raise ValidationError(
            f'Проверьте год ({year}), он не должен быть больше текущего')
    return value
