from django.core.exceptions import ValidationError


def validate_positive(value):
    if value < 1:
        raise ValidationError(
            'Отрицательное число и 0 не допустимо'
        )
