import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from celery import current_app
from myproject.tasks import debug_task

print("🔧 Проверка Celery конфигурации...")
print(f"Broker URL: {current_app.conf.broker_url}")
print(f"Result backend: {current_app.conf.result_backend}")

# Запуск тестовой задачи
print("\n🚀 Запуск тестовой задачи...")
result = debug_task.delay()
print(f"Task ID: {result.id}")

# Попробуем получить результат
try:
    task_result = result.get(timeout=30)
    print(f"✅ Результат: {task_result}")
    print(f"Статус задачи: {result.status}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("Проверьте что Celery Worker запущен")