import re
from datetime import datetime

from django.core.exceptions import ValidationError

from reviews.constants import VALID_USERNAME_REGEX


def validate_username(value):
    """
    Функция для проверки корректности имени пользователя.
    Запрещает использовать "me", и спец. символы, отличные от разрешенных.
    """
    if value.lower() == 'me':
        raise ValidationError(
            'Использование "me" в качестве имени пользователя запрещено.',
            code='invalid_username')

    invalid_chars = re.sub(VALID_USERNAME_REGEX, '', value)

    if invalid_chars:
        raise ValidationError(
            f'Имя пользователя содержит недопустимые символы: {invalid_chars}.'
            'Разрешены только буквы, цифры, и символы @/./+/-/_',
            code='invalid_characters'
        )


def validate_year(value):
    """
    Проверка года выпуска произведения.
    Функция-валидатор проверяет,
    что год произведения не может быть больше текущего года.
    """
    if value > datetime.now().year:
        raise ValidationError(
            "Year of title cannot be greater than the current year"
        )
