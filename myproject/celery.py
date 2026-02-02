import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab

# Установите дефолтные настройки Django для celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# Загрузка настроек из Django settings с префиксом CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач в приложениях
app.autodiscover_tasks()

# Настройка Beat schedule
app.conf.beat_schedule = {
    # ПРОВЕРКА И БЛОКИРОВКА НЕАКТИВНЫХ ПОЛЬЗОВАТЕЛЕЙ
    # Каждый день в 3:00 ночи (после backup в 2:00)
    'block-inactive-users-daily': {
        'task': 'users.tasks.block_inactive_users',  # Или 'api.tasks.block_inactive_users'
        'schedule': crontab(hour=3, minute=0),  # Ежедневно в 03:00
    },

    # Проверка новых платежей каждые 30 минут
    'check-new-payments': {
        'task': 'materials.tasks.check_new_payments',
        'schedule': 1800.0,  # каждые 30 минут (в секундах)
    },

    # Резервное копирование базы данных каждый день в 2:00
    'backup-database': {
        'task': 'myproject.tasks.backup_database',
        'schedule': crontab(hour=2, minute=0),
    },

    # Дополнительно: можно добавить очистку кэша или логирование
    # 'clear-old-logs': {
    #     'task': 'utils.tasks.clear_old_logs',
    #     'schedule': crontab(day_of_week='sunday', hour=4, minute=0),
    # },
}

# Дополнительные настройки
app.conf.timezone = 'Europe/Moscow'
app.conf.task_default_queue = 'default'
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['application/json']


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')