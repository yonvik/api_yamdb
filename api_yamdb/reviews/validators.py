from django.core.exceptions import ValidationError

from .models import MINIMAL_SCORE, MAXIMUM_SCORE


def validate_review_score(value: int):
    if MINIMAL_SCORE > value > MAXIMUM_SCORE:
        raise ValidationError(
            (f'Оценка не может быть меньше {MINIMAL_SCORE} или '
             f'больше {MAXIMUM_SCORE}: {value}')
        )
