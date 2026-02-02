import logging
from typing import Dict, Optional
from django.conf import settings
from django.contrib.auth import get_user_model

from .tasks import send_course_update_email, send_welcome_course_email
from .models import Course, Subscription

logger = logging.getLogger(__name__)
User = get_user_model()


class CourseUpdateService:
    """Сервис для обработки обновлений курса"""

    @staticmethod
    def get_course_changes(old_course_data: Dict, new_course_data: Dict) -> str:
        """
        Определяет изменения между старой и новой версией курса

        Args:
            old_course_data: Данные курса до обновления
            new_course_data: Данные курса после обновления

        Returns:
            Строка с описанием изменений
        """
        changes = []
        tracked_fields = ['name', 'description', 'price', 'stripe_price_id']

        for field in tracked_fields:
            old_value = old_course_data.get(field)
            new_value = new_course_data.get(field)

            if old_value != new_value:
                # Форматируем вывод
                if field == 'price':
                    changes.append(f"💰 Цена изменена: ${old_value} → ${new_value}")
                elif field == 'name':
                    changes.append(f"📝 Название изменено: '{old_value}' → '{new_value}'")
                elif field == 'description':
                    # Разбиваем длинные тернарники для читаемости
                    old_str = str(old_value or '')
                    new_str = str(new_value or '')

                    old_preview = (old_str[:50] + "...") if len(old_str) > 50 else old_str
                    new_preview = (new_str[:50] + "...") if len(new_str) > 50 else new_str

                    changes.append(f"📄 Описание изменено: '{old_preview}' → '{new_preview}'")
                else:
                    changes.append(f"{field}: {old_value} → {new_value}")

        return "\n".join(changes) if changes else None

    @staticmethod
    def send_update_notifications(course_id: int, update_description: str) -> None:
        """
        Постановка задачи на отправку уведомлений об обновлении курса
        """
        # Асинхронная отправка через Celery
        send_course_update_email.delay(
            course_id=course_id,
            update_description=update_description
        )
        logger.info(f"Задача отправки email для курса {course_id} поставлена в очередь")


class SubscriptionService:
    """Сервис для управления подписками"""

    @staticmethod
    def subscribe_user_to_course(user, course) -> Dict:
        """ Подписка пользователя на курс """
        # Создаем или активируем подписку
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            course=course,
            defaults={'is_active': True}
        )

        if not created and not subscription.is_active:
            subscription.is_active = True
            subscription.save()
            created = False  # Подписка уже существовала, просто активировали

        # Отправляем приветственное письмо асинхронно
        if subscription.is_active:
            send_welcome_course_email.delay(course.id, user.id)

        return {
            'subscription': subscription,
            'created': created,
            'message': 'Вы успешно подписались' if created else 'Подписка активирована'
        }

    @staticmethod
    def unsubscribe_user_from_course(user, course) -> Optional[Dict]:
        """ Отписка пользователя от курса """
        try:
            subscription = Subscription.objects.get(user=user, course=course)
            subscription.is_active = False
            subscription.save()

            return {
                'subscription': subscription,
                'message': 'Вы отписались от обновлений курса'
            }
        except Subscription.DoesNotExist:
            return None

    @staticmethod
    def get_course_subscribers(course, user=None) -> Dict:
        """ Получение списка подписчиков курса """
        # Проверка прав доступа
        is_owner = user == course.owner
        is_staff = user and (user.is_staff or user.is_superuser)

        if user and not (is_owner or is_staff):
            raise PermissionError("У вас нет прав для просмотра подписчиков")

        subscriptions = Subscription.objects.filter(
            course=course,
            is_active=True
        ).select_related('user')

        return {
            'course': {
                'id': course.id,
                'name': course.name
            },
            'total_subscribers': subscriptions.count(),
            'subscribers': [
                {
                    'id': sub.user.id,
                    'email': sub.user.email,
                    'subscribed_at': sub.subscribed_at,
                    'is_active': sub.is_active
                }
                for sub in subscriptions
            ]
        }
