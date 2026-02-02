import logging

import shutil
from datetime import datetime

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def backup_database():
    """Создание резервной копии базы данных"""
    logger.info("Начало создания резервной копии базы данных")

    try:
        # Проверка движка базы данных
        db_config = settings.DATABASES['default']

        if db_config['ENGINE'] == 'django.db.backends.sqlite3':
            db_path = db_config['NAME']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{db_path}.backup_{timestamp}"

            # Копируем файл
            shutil.copy2(db_path, backup_path)

            logger.info(f"Резервная копия успешно создана: {backup_path}")
            return f"Backup created: {backup_path}"

        # Логика для других СУБД (PostgreSQL/MySQL) может быть добавлена здесь
        return "Backup skipped: unsupported DB engine"

    except Exception as e:
        logger.error(f"Ошибка при создании резервной копии: {e}")
        return f"Backup failed: {str(e)}"


@shared_task
def debug_task():
    """Тестовая задача для проверки работы Celery"""
    logger.info("Тестовая задача Celery выполнена")
    return "Debug task completed successfully"