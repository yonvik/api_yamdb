from django.core.exceptions import ValidationError

MINIMAL_SCORE = 1
MAXIMUM_SCORE = 10


def validate_review_score(value: int):
    if MINIMAL_SCORE > value or value > MAXIMUM_SCORE:
        raise ValidationError(
            (f'Оценка должна быть больше {MINIMAL_SCORE} и '
             f'меньше {MAXIMUM_SCORE}: {value}')
        )
