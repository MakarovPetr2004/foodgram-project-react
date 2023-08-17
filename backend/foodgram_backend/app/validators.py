from django.core.exceptions import ValidationError


def validate_positive(value):
    if value < 1:
        raise ValidationError(
            'Preparation time must be greater than or equal to 1.'
        )
