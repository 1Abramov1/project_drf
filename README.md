# 📚 Educational Materials API

Django REST Framework API для управления учебными курсами и материалами.

## 🚀 Быстрый старт

```bash
# Клонировать репозиторий
git clone <repo-url>
cd <project>

# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Установить зависимости
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл

# Миграции и суперпользователь
python manage.py migrate
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver

📁 Структура проекта
myproject/
├── api/           # Основное API
├── materials/     # Приложение материалов
├── myproject/     # Настройки
├── requirements.txt
└── manage.py

🔌 Основные API Endpoints

Курсы
GET    /api/materials/courses/     - Список курсов
POST   /api/materials/courses/     - Создать курс

Пример запроса (Postman):
POST http://127.0.0.1:8000/api/materials/courses/
Content-Type: application/json

{
  "title": "Новый курс",
  "description": "Описание курса",
  "owner": 1
}

🛠 Технологии

· Django 4.2+
· Django REST Framework
· PostgreSQL/SQLite
· JWT аутентификация

📄 Лицензия

MIT

**Ещё более минимальная версия:**

```markdown
# Educational Materials API

Django REST API для учебных материалов.

## Установка
```bash
git clone <repo>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

API

· GET/POST /api/materials/courses/ - Работа с курсами
· GET/POST /api/materials/lessons/ - Работа с уроками

Пример создания курса:
POST /api/materials/courses/
{
  "title": "Название",
  "description": "Описание",
  "owner": 1
}

Технологии

· Django REST Framework
· JWT аутентификация

🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте feature ветку (git checkout -b feature/AmazingFeature)
3. Закоммитьте изменения (git commit -m 'Add some AmazingFeature')
4. Запушьте ветку (git push origin feature/AmazingFeature)
5. Откройте Pull Request

📄 Лицензия

Этот проект распространяется под лицензией MIT. Смотрите файл LICENSE для подробностей.

👨‍💻 Автор

Абрамов Алекcандр

· GitHub: @1Abramov1

🙏 Благодарности

· Команда Bootstrap за отличный фреймворк
· Сообщество Python за документацию и примеры
· Все контрибьюторы проекта

---

⭐️ Не забудьте поставить звезду, если проект был полезен!