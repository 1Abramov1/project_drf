from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_weekly_statistics():
    """Отправка еженедельной статистики администраторам"""
    logger.info("Отправка еженедельной статистики")

    admin_users = User.objects.filter(is_staff=True)
    admin_emails = [user.email for user in admin_users if user.email]

    if not admin_emails:
        return "Нет администраторов для отправки статистики"

    # Пример статистики
    total_users = User.objects.count()
    # total_courses = Course.objects.count()  # если импортировать модель

    subject = 'Еженедельная статистика платформы'
    message = f"""
    Еженедельная статистика платформы:

    Всего пользователей: {total_users}
    Всего курсов: 0  # Добавьте логику для курсов

    Статистика за неделю:
    - Новых пользователей: 0
    - Новых курсов: 0
    - Совершено платежей: 0

    С уважением,
    Образовательная платформа
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        admin_emails,
        fail_silently=False,
    )

    return f"Статистика отправлена {len(admin_emails)} администраторам"


@shared_task
def send_welcome_email(user_id):
    """Отправка приветственного письма новому пользователю"""
    try:
        user = User.objects.get(id=user_id)

        subject = 'Добро пожаловать на образовательную платформу!'
        message = f"""
        Здравствуйте, {user.email}!

        Добро пожаловать на нашу образовательную платформу!

        Теперь у вас есть доступ ко всем курсам и материалам.

        С уважением,
        Команда платформы
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return f"Приветственное письмо отправлено пользователю {user.email}"
    except User.DoesNotExist:
        return f"Пользователь с ID {user_id} не найден"