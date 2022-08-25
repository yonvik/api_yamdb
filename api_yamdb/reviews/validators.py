from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers

MINIMAL_SCORE = 1
MAXIMUM_SCORE = 10


def validate_review_score(value: int):
    if MINIMAL_SCORE > value or value > MAXIMUM_SCORE:
        raise ValidationError(
            (f'Оценка должна быть больше {MINIMAL_SCORE} и '
             f'меньше {MAXIMUM_SCORE}: {value}')
        )


def validate_year_title(value):
    year = timezone.datetime.now().year
    if value > timezone.datetime.now().year:
        raise serializers.ValidationError(
            f'Год выпуска не может быть больше {year}'
        )
    return value
