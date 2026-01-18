from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status

from users.models import User
from materials.models import Course, Lesson, Subscription


class LessonCRUDTestCase(TestCase):
    """
    Тесты CRUD операций для уроков.
    """

    def setUp(self):
        """Создание тестовых данных"""
        # Создаем группы
        self.moderator_group, _ = Group.objects.get_or_create(name='moderators')
        self.regular_group, _ = Group.objects.get_or_create(name='regular_users')

        # Создаем пользователей
        self.owner_user = User.objects.create_user(
            email='owner@test.com',
            password='testpass123'
        )

        self.moderator_user = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123'
        )
        self.moderator_user.groups.add(self.moderator_group)

        self.regular_user = User.objects.create_user(
            email='regular@test.com',
            password='testpass123'
        )
        self.regular_user.groups.add(self.regular_group)

        self.other_user = User.objects.create_user(
            email='other@test.com',
            password='testpass123'
        )

        # Создаем курс
        self.course = Course.objects.create(
            title='Тестовый курс',
            description='Описание тестового курса',
            owner=self.owner_user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            title='Тестовый урок',
            description='Описание тестового урока',
            course=self.course,
            owner=self.owner_user,
            video_link='https://www.youtube.com/watch?v=test123'
        )

        self.client = APIClient()

    # --------------------------
    # ТЕСТЫ СОЗДАНИЯ УРОКА
    # --------------------------

    def test_owner_can_create_lesson(self):
        """Владелец может создать урок в своем курсе"""
        self.client.force_authenticate(user=self.owner_user)

        data = {
            'title': 'Новый урок',
            'description': 'Описание нового урока',
            'course': self.course.id,
            'video_link': 'https://www.youtube.com/watch?v=newlesson'
        }

        response = self.client.post('/api/materials/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_moderator_cannot_create_lesson(self):
        """Модератор НЕ может создавать уроки"""
        self.client.force_authenticate(user=self.moderator_user)

        data = {
            'title': 'Урок от модератора',
            'description': 'Модератор пытается создать урок',
            'course': self.course.id,
            'video_link': 'https://www.youtube.com/watch?v=moderator'
        }

        response = self.client.post('/api/materials/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_create_lesson_in_foreign_course(self):
        """Обычный пользователь не может создать урок в чужом курсе"""
        self.client.force_authenticate(user=self.regular_user)

        data = {
            'title': 'Чужой урок',
            'description': 'Попытка создать урок в чужом курсе',
            'course': self.course.id,
            'video_link': 'https://www.youtube.com/watch?v=foreign'
        }

        response = self.client.post('/api/materials/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_creation_with_invalid_youtube_link(self):
        """Нельзя создать урок с не-YouTube ссылкой"""
        self.client.force_authenticate(user=self.owner_user)

        data = {
            'title': 'Урок с плохой ссылкой',
            'description': 'Невалидная ссылка',
            'course': self.course.id,
            'video_link': 'https://vimeo.com/12345'  # Не YouTube!
        }

        response = self.client.post('/api/materials/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

        # --------------------------
        # ТЕСТЫ ЧТЕНИЯ УРОКОВ
        # --------------------------

        def test_owner_can_view_own_lesson(self):
            """Владелец может просматривать свой урок"""
            self.client.force_authenticate(user=self.owner_user)
            response = self.client.get(f'/api/materials/lessons/{self.lesson.id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['title'], self.lesson.title)

        def test_moderator_can_view_any_lesson(self):
            """Модератор может просматривать любой урок"""
            self.client.force_authenticate(user=self.moderator_user)
            response = self.client.get(f'/api/materials/lessons/{self.lesson.id}/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_regular_user_cannot_view_foreign_lesson(self):
            """Обычный пользователь не может просматривать чужой урок"""
            self.client.force_authenticate(user=self.regular_user)
            response = self.client.get(f'/api/materials/lessons/{self.lesson.id}/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        def test_lesson_list_shows_only_accessible_lessons(self):
            """Список уроков показывает только доступные пользователю уроки"""
            # Владелец видит только свои уроки
            self.client.force_authenticate(user=self.owner_user)
            response = self.client.get('/api/materials/lessons/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 1)

            # Модератор видит все уроки
            self.client.force_authenticate(user=self.moderator_user)
            response = self.client.get('/api/materials/lessons/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Здесь будет 1 урок, но в реальности могло бы быть больше

        # --------------------------
        # ТЕСТЫ ОБНОВЛЕНИЯ УРОКОВ
        # --------------------------

        def test_owner_can_update_own_lesson(self):
            """Владелец может обновлять свой урок"""
            self.client.force_authenticate(user=self.owner_user)

            data = {'title': 'Обновленный заголовок'}
            response = self.client.patch(f'/api/materials/lessons/{self.lesson.id}/', data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.lesson.refresh_from_db()
            self.assertEqual(self.lesson.title, 'Обновленный заголовок')

        def test_moderator_can_update_any_lesson(self):
            """Модератор может обновлять любой урок"""
            self.client.force_authenticate(user=self.moderator_user)

            data = {'description': 'Обновлено модератором'}
            response = self.client.patch(f'/api/materials/lessons/{self.lesson.id}/', data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_regular_user_cannot_update_foreign_lesson(self):
            """Обычный пользователь не может обновлять чужой урок"""
            self.client.force_authenticate(user=self.regular_user)

            data = {'title': 'Попытка обновить'}
            response = self.client.patch(f'/api/materials/lessons/{self.lesson.id}/', data)

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # --------------------------
        # ТЕСТЫ УДАЛЕНИЯ УРОКОВ
        # --------------------------

        def test_owner_can_delete_own_lesson(self):
            """Владелец может удалять свой урок"""
            self.client.force_authenticate(user=self.owner_user)

            response = self.client.delete(f'/api/materials/lessons/{self.lesson.id}/')

            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(Lesson.objects.count(), 0)

        def test_moderator_cannot_delete_lesson(self):
            """Модератор НЕ может удалять уроки"""
            self.client.force_authenticate(user=self.moderator_user)

            response = self.client.delete(f'/api/materials/lessons/{self.lesson.id}/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(Lesson.objects.count(), 1)  # Урок остался

        def test_regular_user_cannot_delete_foreign_lesson(self):
            """Обычный пользователь не может удалять чужой урок"""
            self.client.force_authenticate(user=self.regular_user)

            response = self.client.delete(f'/api/materials/lessons/{self.lesson.id}/')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(Lesson.objects.count(), 1)


class SubscriptionTestCase(TestCase):
    """
    Тесты функционала подписок на курсы.
    """

    def setUp(self):
        """Создание тестовых данных"""
        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name='moderators')

        # Создаем пользователей
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123'
        )

        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123'
        )

        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123'
        )
        self.moderator.groups.add(self.moderator_group)

        # Создаем курсы
        self.course1 = Course.objects.create(
            title='Курс 1',
            description='Описание курса 1',
            owner=self.user1
        )

        self.course2 = Course.objects.create(
            title='Курс 2',
            description='Описание курса 2',
            owner=self.user2
        )

        self.client = APIClient()

    # --------------------------
    # ТЕСТЫ ДОБАВЛЕНИЯ ПОДПИСКИ
    # --------------------------

    def test_user_can_subscribe_to_course(self):
        """Пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.user1)

        data = {'course_id': self.course1.id}
        response = self.client.post('/api/materials/subscriptions/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['subscribed'])

        # Проверяем, что подписка создалась в базе
        self.assertTrue(
            Subscription.objects.filter(user=self.user1, course=self.course1).exists()
        )

    def test_user_can_subscribe_to_foreign_course(self):
        """Пользователь может подписаться на чужой курс"""
        self.client.force_authenticate(user=self.user1)

        data = {'course_id': self.course2.id}  # Курс user2
        response = self.client.post('/api/materials/subscriptions/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['subscribed'])

    def test_moderator_can_subscribe(self):
        """Модератор может подписаться на курс"""
        self.client.force_authenticate(user=self.moderator)

        data = {'course_id': self.course1.id}
        response = self.client.post('/api/materials/subscriptions/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['subscribed'])

    def test_subscription_requires_course_id(self):
        """Требуется указать course_id"""
        self.client.force_authenticate(user=self.user1)

        response = self.client.post('/api/materials/subscriptions/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

        def test_subscription_to_nonexistent_course(self):
            """Попытка подписаться на несуществующий курс"""
            self.client.force_authenticate(user=self.user1)

            data = {'course_id': 999}  # Несуществующий ID
            response = self.client.post('/api/materials/subscriptions/', data)

            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # --------------------------
        # ТЕСТЫ УДАЛЕНИЯ ПОДПИСКИ
        # --------------------------

        def test_user_can_unsubscribe_from_course(self):
            """Пользователь может отписаться от курса"""
            # Сначала подписываемся
            subscription = Subscription.objects.create(
                user=self.user1,
                course=self.course1
            )

            self.client.force_authenticate(user=self.user1)
            data = {'course_id': self.course1.id}
            response = self.client.post('/api/materials/subscriptions/', data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Подписка удалена')
            self.assertFalse(response.data['subscribed'])

            # Проверяем, что подписка удалилась
            self.assertFalse(
                Subscription.objects.filter(user=self.user1, course=self.course1).exists()
            )

        def test_subscription_toggle(self):
            """Подписка работает как переключатель (toggle)"""
            self.client.force_authenticate(user=self.user1)
            data = {'course_id': self.course1.id}

            # Первый запрос - добавляем подписку
            response1 = self.client.post('/api/materials/subscriptions/', data)
            self.assertTrue(response1.data['subscribed'])

            # Второй запрос - удаляем подписку
            response2 = self.client.post('/api/materials/subscriptions/', data)
            self.assertFalse(response2.data['subscribed'])

            # Третий запрос - снова добавляем
            response3 = self.client.post('/api/materials/subscriptions/', data)
            self.assertTrue(response3.data['subscribed'])

        # --------------------------
        # ТЕСТЫ ПОЛЯ is_subscribed
        # --------------------------

        def test_is_subscribed_field_in_course_serializer(self):
            """Поле is_subscribed правильно отображает статус подписки"""
            # Пользователь 1 подписывается на курс 1
            Subscription.objects.create(user=self.user1, course=self.course1)

            # Пользователь 1 проверяет курс 1 - должен видеть is_subscribed: true
            self.client.force_authenticate(user=self.user1)
            response = self.client.get(f'/api/materials/courses/{self.course1.id}/')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['is_subscribed'])

            # Пользователь 2 проверяет курс 1 - должен видеть is_subscribed: false
            self.client.force_authenticate(user=self.user2)
            response = self.client.get(f'/api/materials/courses/{self.course1.id}/')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(response.data['is_subscribed'])

        def test_is_subscribed_in_course_list(self):
            """Поле is_subscribed работает в списке курсов"""
            # Создаем подписку
            Subscription.objects.create(user=self.user1, course=self.course1)

            self.client.force_authenticate(user=self.user1)
            response = self.client.get('/api/materials/courses/')

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Находим курс 1 в списке и проверяем is_subscribed
            for course in response.data['results']:
                if course['id'] == self.course1.id:
                    self.assertTrue(course['is_subscribed'])
                elif course['id'] == self.course2.id:
                    self.assertFalse(course['is_subscribed'])

        # --------------------------
        # ТЕСТЫ СПИСКА ПОДПИСОК
        # --------------------------

        def test_user_can_view_own_subscriptions_list(self):
            """Пользователь может просмотреть список своих подписок"""
            # Создаем несколько подписок
            Subscription.objects.create(user=self.user1, course=self.course1)
            Subscription.objects.create(user=self.user1, course=self.course2)
            # Подписка другого пользователя (не должна показываться)
            Subscription.objects.create(user=self.user2, course=self.course1)

            self.client.force_authenticate(user=self.user1)
            response = self.client.get('/api/materials/subscriptions/')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['count'], 2)  # Только подписки user1

        def test_empty_subscriptions_list(self):
            """Пустой список подписок"""
            self.client.force_authenticate(user=self.user1)
            response = self.client.get('/api/materials/subscriptions/')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['count'], 0)
            self.assertEqual(len(response.data['results']), 0)


class PaginationTestCase(TestCase):
    """
    Тесты пагинации.
    """

    def setUp(self):
        """Создание тестовых данных для пагинации"""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )

        # Создаем 15 курсов для тестирования пагинации
        for i in range(1, 16):
            Course.objects.create(
                title=f'Курс {i}',
                description=f'Описание курса {i}',
                owner=self.user
            )

        self.client = APIClient()
        # ВАЖНО: аутентифицируем пользователя!
        self.client.force_authenticate(user=self.user)

    def test_pagination_default_page_size(self):
        """Тест пагинации с размером страницы по умолчанию"""
        response = self.client.get('/api/materials/courses/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем новый формат с 'pagination' ключом
        self.assertIn('pagination', response.data)
        self.assertIn('links', response.data)
        self.assertIn('results', response.data)

        # Проверяем структуру пагинации
        pagination_data = response.data['pagination']
        self.assertIn('count', pagination_data)
        self.assertIn('total_pages', pagination_data)
        self.assertIn('current_page', pagination_data)
        self.assertIn('page_size', pagination_data)

        # Проверяем конкретные значения
        self.assertEqual(pagination_data['count'], 15)
        self.assertEqual(len(response.data['results']), pagination_data['page_size'])

    def test_pagination_with_custom_page_size(self):
        """Тест пагинации с кастомным размером страницы"""
        response = self.client.get('/api/materials/courses/?page_size=5')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем новый формат
        self.assertIn('pagination', response.data)
        pagination_data = response.data['pagination']

        self.assertEqual(pagination_data['page_size'], 5)
        self.assertEqual(pagination_data['total_pages'], 3)  # 15/5=3
        self.assertEqual(len(response.data['results']), 5)

    def test_pagination_page_navigation(self):
        """Тест навигации по страницам"""
        # Первая страница
        response1 = self.client.get('/api/materials/courses/?page_size=5&page=1')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        pagination1 = response1.data['pagination']
        self.assertEqual(pagination1['current_page'], 1)
        self.assertTrue(pagination1['has_next'])
        self.assertFalse(pagination1['has_previous'])
        self.assertIsNotNone(response1.data['links']['next'])
        self.assertIsNone(response1.data['links']['previous'])

        # Вторая страница
        response2 = self.client.get('/api/materials/courses/?page_size=5&page=2')
        pagination2 = response2.data['pagination']
        self.assertEqual(pagination2['current_page'], 2)
        self.assertTrue(pagination2['has_next'])
        self.assertTrue(pagination2['has_previous'])
        self.assertIsNotNone(response2.data['links']['next'])
        self.assertIsNotNone(response2.data['links']['previous'])

        # Последняя страница
        response3 = self.client.get('/api/materials/courses/?page_size=5&page=3')
        pagination3 = response3.data['pagination']
        self.assertEqual(pagination3['current_page'], 3)
        self.assertFalse(pagination3['has_next'])
        self.assertTrue(pagination3['has_previous'])
        self.assertIsNone(response3.data['links']['next'])
        self.assertIsNotNone(response3.data['links']['previous'])

    def test_invalid_page_number(self):
        """Запрос несуществующей страницы"""
        response = self.client.get('/api/materials/courses/?page=99')
        # DRF возвращает 404 для несуществующей страницы
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
