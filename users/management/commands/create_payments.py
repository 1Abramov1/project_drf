from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User, Payment
from materials.models import Course, Lesson
from decimal import Decimal
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Создание тестовых платежей'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Количество платежей для создания (по умолчанию 20)'
        )

    def handle(self, *args, **options):
        count = options['count']

        # Получаем пользователей, курсы и уроки
        users = list(User.objects.all())
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('Нет пользователей. Создайте сначала пользователей.'))
            return

        if not courses and not lessons:
            self.stdout.write(self.style.ERROR('Нет курсов и уроков. Создайте сначала курсы и уроки.'))
            return

        # Создаем платежи
        payments_created = 0

        for i in range(count):
            user = random.choice(users)

            # Случайно выбираем курс или урок
            paid_course = None
            paid_lesson = None

            if courses and random.choice([True, False]):
                paid_course = random.choice(courses)
                amount = Decimal(random.randint(1000, 50000))  # Сумма за курс
            elif lessons:
                paid_lesson = random.choice(lessons)
                amount = Decimal(random.randint(100, 5000))  # Сумма за урок
            elif courses:  # Если нет уроков, но есть курсы
                paid_course = random.choice(courses)
                amount = Decimal(random.randint(1000, 50000))
            else:
                continue  # Пропускаем если нет ни курсов ни уроков

            # Случайный способ оплаты
            payment_method = random.choice([Payment.PaymentMethod.CASH, Payment.PaymentMethod.TRANSFER])

            # Случайная дата (от 30 дней назад до сейчас)
            days_ago = random.randint(0, 30)
            payment_date = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

            # Создаем платеж
            payment = Payment.objects.create(
                user=user,
                payment_date=payment_date,
                paid_course=paid_course,
                paid_lesson=paid_lesson,
                amount=amount,
                payment_method=payment_method
            )

            payments_created += 1

            if paid_course:
                self.stdout.write(f'{i + 1}. {user.email} оплатил курс "{paid_course.title}" на {amount} руб.')
            else:
                self.stdout.write(f'{i + 1}. {user.email} оплатил урок "{paid_lesson.title}" на {amount} руб.')

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {payments_created} платежей')
        )
