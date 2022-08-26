import datetime as dt

from django.core.exceptions import ValidationError

MINIMAL_SCORE = 1
MAXIMUM_SCORE = 10


def validate_review_score(value: int):
    if MINIMAL_SCORE > value or value > MAXIMUM_SCORE:
        raise ValidationError(
            (f'Оценка должна быть больше {MINIMAL_SCORE} и '
             f'меньше {MAXIMUM_SCORE}: {value}')
        )


def validate_title_year(value):
    year = dt.date.today().year
    if value > year:
        raise ValidationError(
            f'Проверьте год ({year}), он не должен быть больше текущего')
    return value
