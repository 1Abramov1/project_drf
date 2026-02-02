import logging
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer

from rest_framework.permissions import IsAuthenticated
from users.permissions import IsOwnerOrModerator, IsOwner, IsNotModerator

from rest_framework.views import APIView

from rest_framework import status
from .models import Subscription
from .serializers import SubscriptionSerializer
from .paginators import MaterialsPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.decorators import api_view, permission_classes
from django.conf import settings
import stripe

from .services import CourseUpdateService, SubscriptionService

logger = logging.getLogger(__name__)


class CourseViewSet(viewsets.ModelViewSet):
    """
        ViewSet для CRUD операций с курсами.

        ### Права доступа:
        - **Создание**: только авторизованные пользователи (становятся владельцами), НЕ модераторы
        - **Просмотр списка**: все авторизованные пользователи
        - **Просмотр деталей**: владелец или модератор
        - **Обновление**: владелец или модератор
        - **Удаление**: только владелец (НЕ модератор)

        ### Особенности:
        - Модераторы видят все курсы, обычные пользователи - только свои
        - При создании курса текущий пользователь автоматически становится владельцем
        """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # Убрал permission_classes по умолчанию, будем определять в get_permissions
    pagination_class = MaterialsPagination

    def get_permissions(self):
        if self.action == 'create':
            # Создание: любой авторизованный, но НЕ модератор (по заданию)
            permission_classes = [IsAuthenticated, IsNotModerator]
        elif self.action == 'destroy':
            # Удаление: только владелец И не модератор
            permission_classes = [IsAuthenticated, IsNotModerator, IsOwner]
        elif self.action in ['update', 'partial_update']:
            # Обновление: (владелец И не модератор) ИЛИ модератор
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'retrieve':
            # Просмотр деталей: (владелец И не модератор) ИЛИ модератор
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        else:  # list
            # Просмотр списка: все авторизованные
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Получить список курсов",
        operation_description="""
            Возвращает список курсов с пагинацией.

            ### Фильтрация:
            - Модераторы видят все курсы
            - Обычные пользователи видят только свои курсы
            """,
        responses={
            200: CourseSerializer(many=True),
            401: "Пользователь не аутентифицирован"
        }
    )
    def list(self, request, *args, **kwargs):
        """Получить список курсов"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создать новый курс",
        operation_description="""
            Создает новый курс. Текущий пользователь автоматически становится владельцем.

            ### Ограничения:
            - Только авторизованные пользователи
            - Модераторы НЕ могут создавать курсы
            """,
        request_body=CourseSerializer,
        responses={
            201: CourseSerializer,
            400: "Неверные данные",
            401: "Пользователь не аутентифицирован",
            403: "Модератор не может создавать курсы"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить детальную информацию о курсе",
        operation_description="""
            Возвращает детальную информацию о курсе по ID.

            ### Права доступа:
            - Владелец курса
            - Модератор
            - Администратор
            """,
        responses={
            200: CourseSerializer,
            401: "Пользователь не аутентифицирован",
            403: "Нет прав для просмотра этого курса",
            404: "Курс не найден"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Полностью обновить курс",
        operation_description="""
            Полностью обновляет курс по ID.

            ### Права доступа:
            - Владелец курса (если не модератор)
            - Модератор
            - Администратор
        """,
        request_body=CourseSerializer,
        responses={
            200: CourseSerializer,
            400: "Неверные данные",
            401: "Пользователь не аутентифицирован",
            403: "Нет прав для обновления этого курса",
            404: "Курс не найден"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частично обновить курс",
        operation_description="""
            Частично обновляет курс по ID (PATCH запрос).

            ### Права доступа:
            - Владелец курса (если не модератор)
            - Модератор
            - Администратор
            """,
        request_body=CourseSerializer,
        responses={
            200: CourseSerializer,
            400: "Неверные данные",
            401: "Пользователь не аутентифицирован",
            403: "Нет прав для обновления этого курса",
            404: "Курс не найден"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить курс",
        operation_description="""
            Удаляет курс по ID.

            ### Ограничения:
            - Только владелец курса
            - Модераторы НЕ могут удалять курсы
            - Администраторы могут удалять любые курсы
            """,
        responses={
            204: "Курс успешно удален",
            401: "Пользователь не аутентифицирован",
            403: "Нет прав для удаления этого курса",
            404: "Курс не найден"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить уроки курса",
        operation_description="""
            Возвращает все уроки, связанные с конкретным курсом.

            ### Права доступа:
            - Владелец курса
            - Модератор
            - Администратор
            """,
        responses={
            200: LessonSerializer(many=True),
            401: "Пользователь не аутентифицирован",
            403: "Нет прав для просмотра уроков этого курса",
            404: "Курс не найден"
        }
    )
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrModerator])
    def lessons(self, request, pk=None):
        """Получить все уроки курса"""
        course = get_object_or_404(Course, pk=pk)
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Подписаться на обновления курса",
        operation_description="""
                Подписаться на получение уведомлений об обновлениях курса.

                После подписки вы будете получать email при любых изменениях курса.
                """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={},
            required=[]
        ),
        responses={
            200: openapi.Response(
                description="Успешная подписка",
                examples={
                    "application/json": {
                        "status": "subscribed",
                        "message": "Вы успешно подписались на обновления курса",
                        "subscription_id": 1,
                        "created": True
                    }
                }
            ),
            401: "Пользователь не аутентифицирован",
            403: "Нет прав для подписки на этот курс"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """
        Подписка на обновления курса
        """
        course = self.get_object()
        user = request.user

        # Проверяем права доступа
        is_allowed = (
                user == course.owner or
                user.is_staff or
                user.is_superuser or
                user.groups.filter(name='moderators').exists()
        )

        if not is_allowed:
            return Response(
                {"error": "У вас нет прав для подписки на этот курс"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Используем сервис для подписки
        from .services import SubscriptionService
        result = SubscriptionService.subscribe_user_to_course(user, course)

        return Response({
            'status': 'subscribed',
            'message': result['message'],
            'subscription_id': result['subscription'].id,
            'created': result['created']
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Отписаться от обновлений курса",
        operation_description="""
                Отписаться от получения уведомлений об обновлениях курса.
                """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={},
            required=[]
        ),
        responses={
            200: openapi.Response(
                description="Успешная отписка",
                examples={
                    "application/json": {
                        "status": "unsubscribed",
                        "message": "Вы отписались от обновлений курса"
                    }
                }
            ),
            401: "Пользователь не аутентифицирован",
            404: "Подписка не найдена"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unsubscribe(self, request, pk=None):
        """
        Отписка от обновлений курса
        """
        course = self.get_object()
        user = request.user

        from .services import SubscriptionService
        result = SubscriptionService.unsubscribe_user_from_course(user, course)

        if result:
            return Response({
                'status': 'unsubscribed',
                'message': result['message']
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Подписка не найдена'
        }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_summary="Получить список подписчиков курса",
        operation_description="""
                Получить список пользователей, подписанных на обновления курса.
                Доступно только для владельца курса или администратора.
                """,
        responses={
            200: openapi.Response(
                description="Список подписчиков",
                examples={
                    "application/json": {
                        "course": {"id": 1, "name": "Python"},
                        "total_subscribers": 3,
                        "subscribers": []
                    }
                }
            ),
            401: "Пользователь не аутентифицирован",
            403: "У вас нет прав для просмотра подписчиков"
        }
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def subscribers(self, request, pk=None):
        """
        Список подписчиков курса
        """
        course = self.get_object()

        try:
            from .services import SubscriptionService
            subscribers_data = SubscriptionService.get_course_subscribers(
                course=course,
                user=request.user
            )
            return Response(subscribers_data)

        except PermissionError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

        except Exception as e:
            logger.error(f"Ошибка получения подписчиков: {e}")
            return Response(
                {'error': 'Внутренняя ошибка сервера'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Тестовая отправка уведомления",
        operation_description="""
                Тестовая отправка уведомления об обновлении курса.

                Доступно только для администраторов.
                """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Текст тестового сообщения"
                )
            },
            required=[]
        ),
        responses={
            200: openapi.Response(
                description="Уведомление поставлено в очередь",
                examples={
                    "application/json": {
                        "status": "test_notification_sent",
                        "message": "Тестовое уведомление поставлено в очередь"
                    }
                }
            ),
            401: "Пользователь не аутентифицирован",
            403: "Только администраторы могут тестировать уведомления"
        }
    )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def test_notification(self, request, pk=None):
        """
        Тестовая отправка уведомления (для администраторов)
        """
        course = self.get_object()

        # Проверяем права (только администраторы)
        if not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {'error': 'Только администраторы могут тестировать уведомления'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Получаем сообщение из запроса или используем по умолчанию
        test_message = request.data.get('message', 'Тестовое обновление курса')

        # Используем сервис для отправки тестового уведомления
        from .services import CourseUpdateService
        CourseUpdateService.send_update_notifications(
            course_id=course.id,
            update_description=test_message
        )

        return Response({
            'status': 'test_notification_sent',
            'message': f'Тестовое уведомление для курса "{course.name}" поставлено в очередь'
        })

    def get_queryset(self):
        """Модераторы видят все курсы, обычные пользователи - только свои"""
        user = self.request.user
        # Проверяем, есть ли у пользователя доступ (аутентифицирован ли он)
        if not user.is_authenticated:
            return Course.objects.none()

        if user.is_staff or user.is_superuser or user.groups.filter(name='moderators').exists():
            # Администраторы и модераторы видят все курсы
            return Course.objects.all()
        else:
            # Обычные пользователи видят только свои курсы
            return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """При создании курса автоматически устанавливаем текущего пользователя как владельца"""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        Переопределяем метод обновления для отправки email подписчикам
        """
        # Сохраняем старые данные курса
        instance = serializer.instance
        old_data = CourseSerializer(instance).data

        # Выполняем обновление
        super().perform_update(serializer)

        # Получаем обновленные данные
        updated_instance = serializer.instance
        new_data = CourseSerializer(updated_instance).data

        # Определяем изменения
        from .services import CourseUpdateService  # Локальный импорт
        changes = CourseUpdateService.get_course_changes(old_data, new_data)

        # Если есть изменения, отправляем email подписчикам асинхронно
        if changes:
            CourseUpdateService.send_update_notifications(
                course_id=updated_instance.id,
                update_description=changes
            )
            logger.info(f"Уведомления об обновлении курса {updated_instance.id} поставлены в очередь")

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrModerator])
    def lessons(self, request, pk=None):
        """Получить все уроки курса"""
        course = get_object_or_404(Course, pk=pk)
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

class LessonListCreateView(generics.ListCreateAPIView):
    """
    Generic View для управления уроками.

    ### Доступные методы:
    - **GET**: Получение списка уроков
    - **POST**: Создание нового урока

    ### Права доступа:
    - **GET**: Все авторизованные пользователи
    - **POST**: Авторизованные пользователи, НЕ модераторы

    ### Особенности:
    - Модераторы видят все уроки
    - Обычные пользователи видят только свои уроки
    - Для создания урока пользователь должен быть владельцем курса
    """

    serializer_class = LessonSerializer
    pagination_class = MaterialsPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            # Создание урока: авторизованный И не модератор
            return [IsAuthenticated(), IsNotModerator()]
        else:  # GET
            # Просмотр списка: авторизованные
            return [IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary="Получить список уроков",
        operation_description="""
           Возвращает список уроков с пагинацией.

           ### Фильтрация по правам:
           - **Модераторы и администраторы**: видят все уроки
           - **Обычные пользователи**: видят только свои уроки

           ### Ответ включает:
           - Список уроков с детальной информацией
           - Пагинационные данные (если включена)
           """,
        responses={
            200: LessonSerializer(many=True),
            401: "Пользователь не аутентифицирован"
        },
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Номер страницы для пагинации",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Количество элементов на странице",
                type=openapi.TYPE_INTEGER,
                default=10
            )
        ]
    )

    def get(self, request, *args, **kwargs):
        """Получить список уроков"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создать новый урок",
        operation_description="""
            Создает новый урок в существующем курсе.

            ### Требования:
            1. Пользователь должен быть авторизован
            2. Пользователь НЕ должен быть модератором
            3. Пользователь должен быть владельцем курса, в который добавляется урок

            ### Обязательные поля:
            - course: ID курса (обязательно)
            - title: Название урока (обязательно)

            ### Пример запроса:

            {
                "course": 1,
                "title": "Новый урок",
                "description": "Описание урока",
                "video_url": "https://example.com/video.mp4"
            }


            ### Ошибки:
            - 400: Неверные данные или отсутствует курс
            - 401: Пользователь не аутентифицирован
            - 403: Пользователь не имеет прав на создание урока в этом курсе
            - 403: Модератор пытается создать урок
            """,  # ИСПРАВЛЕНО: закрывающая тройная кавычка
        request_body=LessonSerializer,
        responses={
            201: LessonSerializer,
            400: openapi.Response(
                description="Неверные данные",
                examples={
                    "application/json": {
                        "course": ["Это поле обязательно."],
                        "title": ["Это поле обязательно."]
                    }
                }
            ),
            401: "Пользователь не аутентифицирован",
            403: openapi.Response(
                description="Ошибка прав доступа",
                examples={
                    "application/json": {
                        "detail": "Вы не можете создавать уроки в курсе 'Название курса'. "
                                  "Владелец курса: owner@example.com"
                    }
                }
            )
        }
    )

    def post(self, request, *args, **kwargs):
        """Создать новый урок"""
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        """Модераторы видят все уроки, обычные пользователи - только свои"""
        # Для Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Lesson.objects.none()

        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.is_staff or user.is_superuser or user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        else:
            return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """При создании урока проверяем права и устанавливаем владельца"""
        # Получаем курс из данных
        course = serializer.validated_data.get('course')

        if not course:
            raise ValidationError("Курс обязателен для создания урока")

        # Проверяем права: только владелец курса может добавлять уроки
        if course.owner != self.request.user:
            raise PermissionDenied(
                f"Вы не можете создавать уроки в курсе '{course.title}'. "
                f"Владелец курса: {course.owner.email}"
            )

        # Сохраняем урок
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic View для получения, обновления и удаления урока.
    Права доступа:
    - Просмотр: владелец или модератор
    - Обновление: владелец или модератор
    - Удаление: только владелец (НЕ модератор)
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            # Удаление: авторизованный И не модератор И владелец
            return [IsAuthenticated(), IsNotModerator(), IsOwner()]
        elif self.request.method in ['PUT', 'PATCH']:
            # Обновление: (владелец И не модератор) ИЛИ модератор
            return [IsAuthenticated(), IsOwnerOrModerator()]
        elif self.request.method == 'GET':
            # Просмотр: (владелец И не модератор) ИЛИ модератор
            return [IsAuthenticated(), IsOwnerOrModerator()]

        return [IsAuthenticated()]

    def perform_update(self, serializer):
        """
        Обновление урока - отправляем уведомление если урок относится к курсу
        """
        # Сохраняем старые данные урока
        instance = serializer.instance
        old_data = LessonSerializer(instance).data

        # Проверяем, есть ли связанный курс
        course = instance.course

        # Выполняем обновление
        super().perform_update(serializer)

        # Получаем обновленные данные
        updated_instance = serializer.instance
        new_data = LessonSerializer(updated_instance).data

        # Если урок относится к курсу и есть изменения
        if course:
            # Определяем изменения в уроке
            changes = []

            for field in ['title', 'description', 'content', 'video_url']:
                old_val = old_data.get(field)
                new_val = new_data.get(field)

                if old_val != new_val:
                    if field == 'title':
                        changes.append(f"Изменено название урока: '{old_val}' → '{new_val}'")

                    elif field == 'description':
                        old_desc = str(old_val or '')[:50]
                        new_desc = str(new_val or '')[:50]

                        if len(str(old_val or '')) > 50:
                            old_desc += "..."
                        if len(str(new_val or '')) > 50:
                            new_desc += "..."

                        changes.append(f"Обновлено описание урока: '{old_desc}' → '{new_desc}'")

                    else:
                        changes.append(f"Обновлен {field}")

            # Если есть изменения в уроке, отправляем уведомление о курсе
            if changes:
                from .services import CourseUpdateService
                update_description = f"Обновлен урок '{updated_instance.title}':\n" + "\n".join(changes)

                CourseUpdateService.send_update_notifications(
                    course_id=course.id,
                    update_description=update_description
                )

                logger.info(f"Уведомление об обновлении урока {updated_instance.id} поставлено в очередь")

    def get_queryset(self):
        """Ограничиваем queryset для не-модераторов"""
        user = self.request.user

        if not user.is_authenticated:
            return Lesson.objects.none()

        # Для GET запросов мы уже проверили права через permissions
        # Но для безопасности все равно фильтруем
        if user.is_staff or user.is_superuser or user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        else:
            return Lesson.objects.filter(owner=user)


class SubscriptionAPIView(APIView):
    """
    API для управления подписками на курсы.
    POST: Добавить/удалить подписку
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Добавить или удалить подписку пользователя на курс.
        Ожидает в теле запроса: {"course_id": <id курса>}
        """
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "Не указан course_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем курс
        course = get_object_or_404(Course, id=course_id)

        # Проверяем существующую подписку
        subscription = Subscription.objects.filter(
            user=user,
            course=course
        ).first()

        if subscription:
            # Если подписка есть - удаляем
            subscription.delete()
            message = 'Подписка удалена'
            subscribed = False
        else:
            # Если подписки нет - создаем
            subscription = Subscription.objects.create(
                user=user,
                course=course
            )
            message = 'Подписка добавлена'
            subscribed = True

        return Response({
            "message": message,
            "subscribed": subscribed,
            "course_id": course.id,
            "course_title": course.title,
            "user_email": user.email
        })

    def get(self, request, *args, **kwargs):
        """
        Получить список подписок текущего пользователя.
        """
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)
        serializer = SubscriptionSerializer(subscriptions, many=True)

        return Response({
            "count": subscriptions.count(),
            "results": serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request, course_id):
    """
    Создание Stripe Checkout сессии для покупки курса
    POST /api/materials/courses/{id}/checkout/
    """
    try:
        # Получаем курс
        course = Course.objects.get(id=course_id)

        # Проверяем, что у курса есть stripe_price_id
        if not course.stripe_price_id:
            return Response(
                {
                    "error": "Для этого курса не настроена цена в Stripe",
                    "detail": "Обратитесь к администратору",
                    "course_id": course_id,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем название курса (проверяем разные варианты названий полей)
        course_name = getattr(course, 'name', None) or getattr(course, 'title', None) or f"Курс {course_id}"
        course_price = getattr(course, 'price', 0)
        course_description = getattr(course, 'description', '')

        # Инициализируем Stripe
        stripe.api_key = settings.STRIPE_API_KEY

        # Создаем сессию Checkout
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': course.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:8000/api/materials/payment/success/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000/api/materials/payment/cancel/',
            client_reference_id=str(request.user.id),
            metadata={
                'course_id': str(course_id),
                'user_id': str(request.user.id),
                'course_name': str(course_name),
                'course_price': str(course_price)
            },
            customer_email=request.user.email
        )

        return Response({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id,
            'session': {
                'id': checkout_session.id,
                'payment_status': checkout_session.payment_status,
                'amount_total': checkout_session.amount_total,
                'currency': checkout_session.currency
            },
            'course': {
                'id': course.id,
                'name': str(course_name),
                'price': str(course_price),
                'stripe_price_id': course.stripe_price_id
            }
        }, status=status.HTTP_200_OK)

    except Course.DoesNotExist:
        return Response(
            {
                "error": "Курс не найден",
                "detail": f"Курс с ID {course_id} не существует"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    except stripe.error.StripeError as e:
        return Response(
            {
                "error": "Ошибка платежной системы",
                "detail": str(e),
                "stripe_error": e.code if hasattr(e, 'code') else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {
                "error": "Внутренняя ошибка сервера",
                "detail": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )