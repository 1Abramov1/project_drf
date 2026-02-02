"""
Настройки проекта Django REST Framework для образовательной платформы.

Основные компоненты:
- Django REST Framework с JWT аутентификацией
- Celery + Redis для асинхронных задач
- Stripe для обработки платежей
- Кастомная модель пользователя (email вместо username)
- Система курсов, уроков и подписок
- Swagger документация API

Переменные окружения загружаются из .env файла
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
from celery.schedules import crontab

# ================ ПУТИ И БАЗОВЫЕ НАСТРОЙКИ ================

# Базовый путь к проекту
BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка переменных окружения из .env файла
load_dotenv()

# Секретный ключ Django (из переменных окружения или fallback)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-development-only')

# Режим отладки (True для разработки, False для продакшена)
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Разрешенные хосты (для продакшена нужно указать реальные домены)
ALLOWED_HOSTS = []

# ================ ПРИЛОЖЕНИЯ И МИДЛВАРЫ ================

INSTALLED_APPS = [
    # Встроенные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Сторонние приложения
    'rest_framework',  # Django REST Framework
    'rest_framework_simplejwt',  # JWT аутентификация
    'django_filters',  # Фильтрация данных
    'django_extensions',  # Дополнительные команды Django
    'drf_yasg',  # Swagger документация

    # Приложения для Celery
    'django_celery_beat',  # Периодические задачи
    'django_celery_results',  # Хранение результатов задач

    # Приложения проекта
    'api',  # API endpoints
    'users',  # Пользователи и аутентификация
    'materials',  # Курсы, уроки и подписки
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# ================ БАЗА ДАННЫХ ================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # SQLite для разработки
    }
}

# ================ ВАЛИДАЦИЯ ПАРОЛЕЙ ================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ================ МЕЖДУНАРОДНЫЕ НАСТРОЙКИ ================

LANGUAGE_CODE = 'en-us'  # Язык интерфейса
TIME_ZONE = 'UTC'  # Часовой пояс
USE_I18N = True  # Интернационализация
USE_TZ = True  # Поддержка часовых поясов

# ================ СТАТИЧЕСКИЕ ФАЙЛЫ И МЕДИА ================

STATIC_URL = 'static/'  # URL для статических файлов
STATIC_ROOT = BASE_DIR / 'staticfiles'    # Путь для сбора статики
MEDIA_URL = '/media/'                     # URL для медиа файлов
MEDIA_ROOT = BASE_DIR / 'media'          # Путь для хранения медиа

# ================ DJANGO REST FRAMEWORK ================

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Временно разрешаем всё
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT токены
        'rest_framework.authentication.SessionAuthentication',       # Сессии
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # Количество элементов на странице
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # Фильтрация
        'rest_framework.filters.OrderingFilter',              # Сортировка
        'rest_framework.filters.SearchFilter',                # Поиск
    ],
}

# ================ КАСТОМНАЯ МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ ================

AUTH_USER_MODEL = 'users.User'  # Используем кастомную модель пользователя

# ================ JWT НАСТРОЙКИ ================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),   # Время жизни access токена
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),      # Время жизни refresh токена
    'ROTATE_REFRESH_TOKENS': False,                   # Вращение refresh токенов
    'BLACKLIST_AFTER_ROTATION': True,                 # Блэклист старых токенов
}

# ================ STRIPE НАСТРОЙКИ ================

STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY')          # Секретный ключ Stripe
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')  # Публичный ключ Stripe

# Проверка загрузки ключей Stripe
if not STRIPE_API_KEY:
    print("⚠️  ВНИМАНИЕ: STRIPE_SECRET_KEY не найден в переменных окружения")
    # В режиме разработки можно продолжать без Stripe

# ================ REDIS НАСТРОЙКИ ================

# Настройки подключения к Redis (брокер для Celery)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')    # Хост Redis
REDIS_PORT = os.getenv('REDIS_PORT', '6379')         # Порт Redis
REDIS_DB = os.getenv('REDIS_DB', '0')               # Номер базы данных
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')    # Пароль (если требуется)

# Формирование URL для подключения к Redis
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# ================ CELERY НАСТРОЙКИ ================

# Конфигурация Celery для асинхронных задач
CELERY_BROKER_URL = REDIS_URL                          # Брокер сообщений (Redis)
CELERY_RESULT_BACKEND = 'django-db'                    # Хранение результатов в БД Django
CELERY_ACCEPT_CONTENT = ['application/json']           # Формат сообщений
CELERY_TASK_SERIALIZER = 'json'                        # Сериализация задач
CELERY_RESULT_SERIALIZER = 'json'                      # Сериализация результатов
CELERY_TIMEZONE = TIME_ZONE                            # Часовой пояс
CELERY_ENABLE_UTC = True                               # Использование UTC

# ================ EMAIL НАСТРОЙКИ ================

# Конфигурация отправки email для уведомлений
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# Настройки SMTP (если используется)
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Настройки file-based backend (для сохранения писем в файлы)
elif EMAIL_BACKEND == 'django.core.mail.backends.filebased.EmailBackend':
    EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
# Создание директории если не существует
    os.makedirs(EMAIL_FILE_PATH, exist_ok=True)

# ================ CELERY BEAT РАСПИСАНИЕ ================

# Планировщик периодических задач
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Расписание периодических задач
CELERY_BEAT_SCHEDULE = {
    # Проверка активности курсов каждый день в 3:00
    'check-courses-activity': {
        'task': 'materials.tasks.check_courses_activity',
        'schedule': crontab(hour=3, minute=0),
        'args': (),
    },
    # Отправка статистики каждый понедельник в 9:00
    'send-weekly-stats': {
        'task': 'users.tasks.send_weekly_statistics',
        'schedule': crontab(day_of_week='monday', hour=9, minute=0),
        'args': (),
    },
    # Очистка старых Stripe сессий каждый день в 4:30
    'cleanup-old-stripe-sessions': {
        'task': 'materials.tasks.cleanup_old_stripe_sessions',
        'schedule': crontab(hour=4, minute=30),
        'args': (),
    },
    # Тестовая задача отправки email каждые 30 минут
    'test-email-task': {
        'task': 'materials.tasks.send_course_update_email',
        'schedule': crontab(minute='*/30'),
        'args': (1, 'Тестовое обновление курса'),
    },
}

# ================ ЛОГИРОВАНИЕ ================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'materials': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# ================ ОТЛАДОЧНАЯ ИНФОРМАЦИЯ ================

# Вывод информации о текущих настройках (только при запуске)
print(f"✅ Режим отладки: {DEBUG}")
print(f"✅ Stripe API ключ: {'Загружен' if STRIPE_API_KEY else 'Не загружен'}")
print(f"✅ Redis URL: {REDIS_URL}")
print(f"✅ Email Backend: {EMAIL_BACKEND}")
print(f"✅ Отправитель email по умолчанию: {DEFAULT_FROM_EMAIL}")