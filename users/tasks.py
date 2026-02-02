import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q

from celery import shared_task

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3)
def block_inactive_users(self):
    """
    Блокирует пользователей, которые не заходили более месяца.
    """
    try:
        logger.info("Запуск задачи блокировки неактивных пользователей...")

        month_ago = timezone.now() - timedelta(days=30)

        # Исправлено: используем Q-объекты для корректной фильтрации через OR
        inactive_users = User.objects.filter(
            Q(last_login__lt=month_ago) | Q(last_login__isnull=True),
            is_active=True
        )

        # Опционально: исключаем стафф
        # inactive_users = inactive_users.exclude(is_superuser=True).exclude(is_staff=True)

        count = inactive_users.count()

        if count == 0:
            logger.info("Неактивных пользователей для блокировки не найдено")
            return {
                "status": "success",
                "message": "Неактивных пользователей не найдено",
                "blocked_count": 0
            }

        user_data = list(inactive_users.values('id', 'email', 'username', 'last_login'))
        user_ids = [user['id'] for user in user_data]

        # Массовое обновление
        inactive_users.update(is_active=False)

        logger.info(f"Заблокировано {count} неактивных пользователей")
        for user in user_data:
            logger.info(f"  - ID: {user['id']}, Email: {user['email']}, Last login: {user['last_login']}")

        try:
            admin_emails = list(
                User.objects.filter(is_staff=True)
                .exclude(email='')
                .values_list('email', flat=True)
            )

            if admin_emails:
                send_admin_notification.delay(count, user_ids, admin_emails)
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление администраторам: {e}")

        return {
            "status": "success",
            "message": f"Заблокировано {count} пользователей",
            "blocked_count": count,
            "blocked_user_ids": user_ids,
            "details": user_data
        }

    except Exception as exc:
        logger.error(f"Ошибка при блокировке пользователей: {str(exc)}")
        raise self.retry(exc=exc, countdown=600)


@shared_task
def send_admin_notification(blocked_count, user_ids, admin_emails):
    """
    Отправляет уведомление администраторам о заблокированных пользователях
    """
    try:
        subject = f'Отчет о блокировке неактивных пользователей ({blocked_count})'
        message = (
            f"Отчет о блокировке неактивных пользователей\n\n"
            f"Всего заблокировано пользователей: {blocked_count}\n"
            f"ID заблокированных пользователей: {user_ids}\n"
            f"Задача выполнена: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Пользователи были заблокированы из-за неактивности.\n\n"
            f"С уважением,\nСистема автоматической модерации"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Ошибка в send_admin_notification: {e}")
        raise

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