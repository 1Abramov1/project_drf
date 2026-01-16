from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from materials.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создает группы модераторов и заполняет их правами'

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderators_group, created = Group.objects.get_or_create(name='moderators')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "moderators" создана'))
        else:
            self.stdout.write('Группа "moderators" уже существует')

        # Получаем разрешения для моделей Course и Lesson
        course_content_type = ContentType.objects.get_for_model(Course)
        lesson_content_type = ContentType.objects.get_for_model(Lesson)

        # Разрешения для модераторов (всё кроме удаления и создания)
        moderator_permissions = [
            # Course permissions
            Permission.objects.get(codename='view_course', content_type=course_content_type),
            Permission.objects.get(codename='change_course', content_type=course_content_type),
            # Lesson permissions
            Permission.objects.get(codename='view_lesson', content_type=lesson_content_type),
            Permission.objects.get(codename='change_lesson', content_type=lesson_content_type),
        ]

        # Добавляем разрешения группе
        moderators_group.permissions.set(moderator_permissions)

        # Создаем группу для обычных пользователей (если нужно)
        users_group, created = Group.objects.get_or_create(name='users')

        if created:
            user_permissions = [
                Permission.objects.get(codename='view_course', content_type=course_content_type),
                Permission.objects.get(codename='view_lesson', content_type=lesson_content_type),
                Permission.objects.get(codename='add_course', content_type=course_content_type),
                Permission.objects.get(codename='add_lesson', content_type=lesson_content_type),
                Permission.objects.get(codename='change_course', content_type=course_content_type),
                Permission.objects.get(codename='change_lesson', content_type=lesson_content_type),
                Permission.objects.get(codename='delete_course', content_type=course_content_type),
                Permission.objects.get(codename='delete_lesson', content_type=lesson_content_type),
            ]
            users_group.permissions.set(user_permissions)
            self.stdout.write(self.style.SUCCESS('Группа "users" создана'))

        self.stdout.write(self.style.SUCCESS('Группы успешно созданы и настроены!'))
