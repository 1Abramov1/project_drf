Django REST Framework: Образовательная платформа

API для управления курсами, уроками, платежами и пользователями.

🚀 Быстрый старт
# Установка
git clone <repo-url>
cd project_drf
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser

# Запуск Redis для Celery
docker run -d -p 6379:6379 redis:alpine

# Запуск сервисов (в разных терминалах)
python manage.py runserver              # Терминал 1
celery -A myproject worker --loglevel=info  # Терминал 2
celery -A myproject beat --loglevel=info    # Терминал 3

📦 Основные функции

🔐 Аутентификация

· JWT токены (email вместо username)
· Роли: пользователь, модератор, администратор
· Автоматическая блокировка неактивных пользователей

📚 Контент

· Курсы и уроки с пагинацией
· Подписки на курсы
· Права доступа к материалам

💳 Платежи

· Интеграция со Stripe
· Онлайн-оплата курсов
· История платежей

⚙️ Фоновые задачи (Celery)

· 3:00 ежедневно - Блокировка неактивных пользователей (30+ дней)
· 9:00 понедельник - Статистика администраторам
· Каждые 30 минут - Проверка платежей
· 2:00 ежедневно - Резервное копирование БД

🔌 Основные эндпоинты

Метод Эндпоинт Описание
POST /api/users/token/ Получение JWT токена
GET /api/materials/courses/ Список курсов
POST /api/materials/courses/{id}/checkout/ Оплата курса (Stripe)
GET /api/users/payments/ История платежей

🛠 Технологии

· Django 4.2 + DRF
· JWT аутентификация
· Stripe API
· Celery + Redis (фоновые задачи)
· SQLite/PostgreSQL

📋 Модели

· Course: курсы с ценами и Stripe интеграцией
· Lesson: уроки курсов
· CustomUser: пользователи с email входом
· Payment: платежи и история
· Subscription: подписки на курсы

🧪 Тестирование
python manage.py test
coverage run manage.py test
coverage report

⚡️ Быстрые команды
# Создать тестового пользователя
python manage.py shell_plus
from django.utils import timezone
from datetime import timedelta
user = get_user_model().objects.create_user(email='test@test.com', password='test123')
user.last_login = timezone.now() - timedelta(days=35)
user.save()

# Запустить задачу вручную
from users.tasks import block_inactive_users
block_inactive_users.delay()

🔧 Настройка .env
DEBUG=True
SECRET_KEY=ваш-ключ
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
REDIS_HOST=localhost
TIME_ZONE=Europe/Moscow

---

Лицензия: MIT
Автор: Александр Абрамов
Версия: 2.0

⭐️ Не забудьте поставить звезду, если проект был полезеy!
