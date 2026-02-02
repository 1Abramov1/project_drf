from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Course
import logging

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def check_courses_activity():
    """Проверка активности курсов и отключение неактивных"""
    logger.info("Запущена проверка активности курсов")

    # Пример: отключаем курсы старше 30 дней без обновлений
    cutoff_date = timezone.now() - timedelta(days=30)
    inactive_courses = Course.objects.filter(
        created_at__lt=cutoff_date,
        is_active=True 
    )

    count = inactive_courses.count()
    # if hasattr(Course, 'is_active'):
    #     inactive_courses.update(is_active=False)

    logger.info(f"Найдено {count} неактивных курсов")
    return f"Проверено курсов: {count}"


@shared_task
def cleanup_old_stripe_sessions():
    """Очистка старых Stripe сессий"""
    logger.info("Запущена очистка старых Stripe сессий")

    # Здесь можно добавить логику очистки устаревших сессий
    # Например, удаление старых записей из базы данных

    return "Очистка Stripe сессий завершена"


@shared_task
def check_new_payments():
    """Проверка новых платежей"""
    logger.info("Проверка новых платежей")

    # Здесь можно добавить логику проверки платежей
    # Например, синхронизация со Stripe API

    return "Проверка платежей завершена"


@shared_task
def send_course_update_notifications(course_id):
    """Отправка уведомлений об обновлении курса"""
    from .models import Course
    # Логика отправки уведомлений
    return f"Уведомления отправлены для курса {course_id}"


@shared_task
def send_course_update_email(course_id, update_description=None):
    """
    Асинхронная отправка email подписчикам об обновлении курса
    """
    from .models import Course, Subscription

    try:
        # Получаем курс
        course = Course.objects.get(id=course_id)

        # Получаем всех активных подписчиков курса
        subscriptions = Subscription.objects.filter(
            course=course,
            is_active=True
        ).select_related('user')

        if not subscriptions.exists():
            logger.info(f"Нет подписчиков для курса {course.name}")
            return "Нет подписчиков для отправки"

        # Подготовка списка email
        recipient_list = []
        for subscription in subscriptions:
            if subscription.user.email:
                recipient_list.append(subscription.user.email)

        if not recipient_list:
            logger.warning(f"У подписчиков курса {course.name} нет email")
            return "Нет email адресов для отправки"

        # Тема письма
        subject = f'Обновление курса: {course.name}'

        # Текст письма
        if update_description:
            message = f"""
            Здравствуйте!

            Курс "{course.name}" был обновлен.

            Что нового:
            {update_description}

            Посмотреть обновления: http://localhost:8000/api/materials/courses/{course.id}/

            С уважением,
            Команда образовательной платформы
            """
        else:
            message = f"""
            Здравствуйте!

            Курс "{course.name}" был обновлен.

            Посмотреть обновления: http://localhost:8000/api/materials/courses/{course.id}/

            С уважением,
            Команда образовательной платформы
            """

        # Отправка email
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        logger.info(f"Отправлено писем: {len(recipient_list)} для курса '{course.name}'")
        return f"Отправлено {len(recipient_list)} писем подписчикам курса '{course.name}'"

    except Course.DoesNotExist:
        logger.error(f"Курс с ID {course_id} не найден")
        return f"Курс с ID {course_id} не найден"
    except Exception as e:
        logger.error(f"Ошибка отправки email для курса {course_id}: {str(e)}")
        return f"Ошибка: {str(e)}"


@shared_task
def send_welcome_course_email(course_id, user_id):
    """
    Отправка приветственного письма при подписке на курс
    """
    try:
        from .models import Course
        from django.contrib.auth.models import User  # Не забудь импорт User

        course = Course.objects.get(id=course_id)
        user = User.objects.get(id=user_id)

        if not user.email:
            return f"У пользователя {user.username} нет email"

        subject = f'Вы подписались на курс: {course.name}'
        message = f"""
        Здравствуйте, {user.email}!

        Вы успешно подписались на курс "{course.name}".

        Описание курса: {course.description[:100]}...

        Начать обучение: http://localhost:8000/api/materials/courses/{course.id}/

        С уважением,
        Команда образовательной платформы
        """

        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return f"Приветственное письмо отправлено {user.email} для курса {course.name}"

    except Exception as e:
        return f"Ошибка отправки приветственного письма: {str(e)}"
