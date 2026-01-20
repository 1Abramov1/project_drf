from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


class YouTubeURLValidator:
    """
    Валидатор для проверки, что ссылка ведет на YouTube.
    Разрешает только ссылки формата:
    - https://www.youtube.com/
    - https://youtube.com/
    - https://youtu.be/ (сокращенные ссылки)
    """

    def __init__(self, field='video_link'):
        self.field = field

    def __call__(self, value):
        if not value:
            return  # Пустое значение разрешено

        # Проверяем, что ссылка ведет на YouTube
        youtube_patterns = [
            r'^https?://(www\.)?youtube\.com/',
            r'^https?://youtu\.be/',
            r'^https?://m\.youtube\.com/',  # мобильная версия
        ]

        is_youtube_url = any(re.match(pattern, value) for pattern in youtube_patterns)

        if not is_youtube_url:
            raise ValidationError(
                _('Ссылка должна вести на YouTube. Пример: https://www.youtube.com/watch?v=... или https://youtu.be/...'),
                code='invalid_url'
            )


# Альтернативно: функция-валидатор
def validate_youtube_url(value):
    """
    Функция-валидатор для проверки YouTube ссылок.
    """
    if not value:
        return

    youtube_patterns = [
        r'^https?://(www\.)?youtube\.com/',
        r'^https?://youtu\.be/',
        r'^https?://m\.youtube\.com/',
    ]

    is_youtube_url = any(re.match(pattern, value) for pattern in youtube_patterns)

    if not is_youtube_url:
        raise ValidationError(
            'Ссылка должна вести на YouTube. Пример: https://www.youtube.com/watch?v=... или https://youtu.be/...'
        )
