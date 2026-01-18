from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer

from rest_framework.permissions import IsAuthenticated
from users.permissions import IsOwnerOrModerator, IsOwner, IsNotModerator

from rest_framework.views import APIView

from rest_framework import status
from .models import Subscription
from .serializers import SubscriptionSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с курсами.
    Права доступа:
    - Создание: только авторизованные пользователи (становятся владельцами)
    - Просмотр списка: все авторизованные
    - Просмотр деталей: владелец или модератор
    - Обновление: владелец или модератор
    - Удаление: только владелец (НЕ модератор)
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # Убрали permission_classes по умолчанию, будем определять в get_permissions

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

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrModerator])
    def lessons(self, request, pk=None):
        """Получить все уроки курса"""
        course = get_object_or_404(Course, pk=pk)
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonListCreateView(generics.ListCreateAPIView):
    """
    Generic View для получения списка уроков и создания нового.
    Права доступа:
    - Создание: только авторизованные пользователи
    - Просмотр списка: все авторизованные (фильтруется по владельцу в get_queryset)
    """
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            # Создание урока: авторизованный И не модератор
            return [IsAuthenticated(), IsNotModerator()]
        else:  # GET
            # Просмотр списка: авторизованные
            return [IsAuthenticated()]

    def get_queryset(self):
        """Модераторы видят все уроки, обычные пользователи - только свои"""
        user = self.request.user

        # Проверяем, есть ли у пользователя доступ (аутентифицирован ли он)
        if not user.is_authenticated:
            return Lesson.objects.none()

        if user.is_staff or user.is_superuser or user.groups.filter(name='moderators').exists():
            # Администраторы и модераторы видят все уроки
            return Lesson.objects.all()
        else:
            # Обычные пользователи видят только свои уроки
            return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """При создании урока автоматически устанавливаем текущего пользователя как владельца"""
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
