Вот обновленный файл README.md с информацией о выполненных заданиях:
# 📚 Educational Materials API

Django REST Framework API для управления учебными курсами, уроками и платежами.

## 🚀 Быстрый старт

```bash
# Клонировать репозиторий
git clone <repo-url>
cd project_drf

# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver

📁 Структура проекта
project_drf/
├── api/           # Основное API
├── materials/     # Курсы и уроки
├── users/         # Пользователи и платежи
├── myproject/     # Настройки проекта
├── requirements.txt
├── manage.py
└── README.md

✅ Выполненные задания

Задание 1: Кастомная модель пользователя

· Авторизация по email вместо username
· Дополнительные поля: телефон, город, аватарка
· Кастомный UserManager

Задание 2: Модель платежей (Payment)

· Связь с пользователем, курсом или уроком
· Поля: дата оплаты, сумма, способ оплаты (наличные/перевод)
· Фикстуры с тестовыми данными
· Админ-панель для управления

Задание 3: CRUD API

· Курсы: ViewSet с полным CRUD
· Уроки: Generic Views (ListCreateAPIView, RetrieveUpdateDestroyAPIView)
· Сериализаторы: CourseSerializer с уроками и lesson_count
· Все операции доступны через API

Задание 4: Фильтрация платежей

· Сортировка по дате оплаты (возрастание/убывание)
· Фильтрация по курсу или уроку
· Фильтрация по способу оплаты
· Использование django-filter для расширенной фильтрации

🔌 Основные API Endpoints

Курсы (ViewSet)
GET    /api/materials/courses/          - Список курсов
POST   /api/materials/courses/          - Создать курс
GET    /api/materials/courses/{id}/     - Получить курс
PUT    /api/materials/courses/{id}/     - Обновить курс
PATCH  /api/materials/courses/{id}/     - Частично обновить
DELETE /api/materials/courses/{id}/     - Удалить курс
GET    /api/materials/courses/{id}/lessons/ - Уроки курса

Уроки (Generic Views)
GET    /api/materials/lessons/          - Список уроков
POST   /api/materials/lessons/          - Создать урок
GET    /api/materials/lessons/{id}/     - Получить урок
PUT    /api/materials/lessons/{id}/     - Обновить урок
DELETE /api/materials/lessons/{id}/     - Удалить урок

Платежи (с фильтрацией)
GET    /api/users/payments/             - Все платежи
GET    /api/users/payments/?payment_method=cash      - Только наличные
GET    /api/users/payments/?payment_method=transfer  - Только переводы
GET    /api/users/payments/?paid_course=1            - За курс 1
GET    /api/users/payments/?paid_lesson=1            - За урок 1
GET    /api/users/payments/?ordering=payment_date    - По дате (старые)
GET    /api/users/payments/?ordering=-payment_date   - По дате (новые)

📝 Примеры запросов

Создание курса (Postman)
POST http://127.0.0.1:8000/api/materials/courses/
Content-Type: application/json

{
  "title": "Django для начинающих",
  "description": "Полный курс по Django и DRF",
  "owner": 1
}

Создание урока
POST http://127.0.0.1:8000/api/materials/lessons/
Content-Type: application/json

{
  "title": "Введение в Django",
  "description": "Основные концепции Django",
  "course": 1,
  "video_link": "https://youtube.com/watch?v=example",
  "owner": 1
}

🛠 Технологии

· Django 4.2+ - веб-фреймворк
· Django REST Framework - построение API
· django-filter - фильтрация данных
· SQLite - база данных (разработка)
· Pillow - работа с изображениями

⚙️ Настройки

Основные настройки в myproject/settings.py:
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

AUTH_USER_MODEL = 'users.User'

📦 Зависимости
Django==4.2.0
djangorestframework==3.14.0
django-filter==23.3
Pillow==10.0.0

🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте feature ветку (git checkout -b feature/AmazingFeature)
3. Закоммитьте изменения (git commit -m 'Add some AmazingFeature')
4. Запушьте ветку (git push origin feature/AmazingFeature)
5. Откройте Pull Request

📄 Лицензия

Этот проект распространяется под лицензией MIT.

👨‍💻 Автор

Александр Абрамов

🙏 Благодарности

· Команда Django за отличный фреймворк
· Сообщество Django REST Framework
· Все контрибьюторы проекта

---

⭐️ Не забудьте поставить звезду, если проект был полезен!