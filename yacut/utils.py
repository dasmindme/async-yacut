import random
import string

from .models import URLMap

ALPHABET = string.ascii_letters + string.digits
RESERVED = {"files"}


def get_unique_short_id(
    min_length: int = 6,
    max_length: int = 16,
    attempts_per_length: int = 50,
) -> str:
    """
    Генерирует уникальный short_id переменной длины.
    Сначала пробует min_length, при частых коллизиях увеличивает длину,
    но не превышает max_length.
    """
    for length in range(min_length, max_length + 1):
        for _ in range(attempts_per_length):
            short_id = "".join(random.choice(ALPHABET) for _ in range(length))

            if short_id in RESERVED:
                continue

            if not URLMap.query.filter_by(short=short_id).first():
                return short_id

    raise RuntimeError("Не удалось сгенерировать уникальный short_id")