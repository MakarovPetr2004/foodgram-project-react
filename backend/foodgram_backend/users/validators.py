import re

from constants import USERNAME_PATTERN
from rest_framework.exceptions import ValidationError


def regex_validator(value):
    invalid_chars = ''.join(set(re.sub(USERNAME_PATTERN, '', value)))
    if invalid_chars:
        error_message = (f'Username contains invalid characters:'
                         f' {invalid_chars}')
        raise ValidationError(error_message)
    return value


class UsernameValidationMixin:
    def validate_username(self, value):
        return regex_validator(value)
