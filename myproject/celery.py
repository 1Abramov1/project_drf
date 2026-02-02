import os
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
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')