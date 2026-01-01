import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from users.models import User
from materials.models import Course, Lesson

# Создаем тестового пользователя
user = User.objects.create_user(
    email='teacher@example.com',
    password='testpass123',
    first_name='Иван',
    last_name='Преподаватель'
)

# Создаем курсы
courses_data = [
    {
        'title': 'Django для начинающих',
        'description': 'Полный курс по разработке на Django и DRF',
        'owner': user
    },
    {
        'title': 'Python продвинутый',
        'description': 'Продвинутые темы Python',
        'owner': user
    },
    {
        'title': 'Веб-разработка',
        'description': 'Курс по веб-разработке',
        'owner': user
    },
]

created_courses = []
for course_data in courses_data:
    course = Course.objects.create(**course_data)
    created_courses.append(course)
    print(f"Создан курс: {course.title}")

# Создаем уроки для каждого курса
lessons_data = [
    # Уроки для первого курса
    {'title': 'Введение в Django', 'description': 'Основные концепции', 'course': created_courses[0], 'owner': user},
    {'title': 'Модели Django', 'description': 'Работа с моделями', 'course': created_courses[0], 'owner': user},
    {'title': 'Django REST Framework', 'description': 'Создание API', 'course': created_courses[0], 'owner': user},

    # Уроки для второго курса
    {'title': 'Декораторы Python', 'description': 'Продвинутые декораторы', 'course': created_courses[1],
     'owner': user},
    {'title': 'Многопоточность', 'description': 'Работа с потоками', 'course': created_courses[1], 'owner': user},

    # Уроки для третьего курса
    {'title': 'HTML/CSS основы', 'description': 'Верстка сайтов', 'course': created_courses[2], 'owner': user},
    {'title': 'JavaScript', 'description': 'Основы JavaScript', 'course': created_courses[2], 'owner': user},
    {'title': 'React.js', 'description': 'Фронтенд фреймворк', 'course': created_courses[2], 'owner': user},
]

for lesson_data in lessons_data:
    lesson = Lesson.objects.create(**lesson_data)
    print(f"Создан урок: {lesson.title} (Курс: {lesson.course.title})")

print(f"\n✅ Создано: {Course.objects.count()} курсов, {Lesson.objects.count()} уроков")
