from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import filters, viewsets, status
from django_filters import rest_framework as django_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Payment, User
from .filters import PaymentFilter
from .serializers import UserSerializer, UserRegistrationSerializer, PaymentSerializer
from users.permissions import IsOwnerOrModerator, IsOwner, IsNotModerator



class UserRegistrationView(APIView):
    """Отдельный View для регистрации, полностью публичный"""
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Регистрация нового пользователя",
        operation_description="""
        Создает нового пользователя и возвращает JWT токены для автоматической авторизации.

        ### Обязательные поля:
        - email: Email пользователя (уникальный)
        - password: Пароль пользователя
        - password2: Подтверждение пароля

        ### Опциональные поля:
        - phone: Телефон
        - city: Город
        - avatar: URL аватара

        ### Пример запроса:
               {
            "email": "user@example.com",
            "password": "securepassword123",
            "password2": "securepassword123",
            "phone": "+79991234567",
            "city": "Москва"
        }
                """,
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Пользователь успешно создан",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                'city': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Неверные данные"
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления платежами.

    ### Особенности:
    - Все операции требуют JWT-авторизации
    - Пользователи видят только свои платежи
    - Администраторы видят все платежи
    - Доступна фильтрация и сортировка

    ### Фильтрация:
    - По курсу: ?paid_course=1
    - По уроку: ?paid_lesson=2
    - По способу оплаты: ?payment_method=cash
    - По дате: ?payment_date_after=2024-01-01&payment_date_before=2024-12-31

    ### Сортировка:
    - По дате оплаты: ?ordering=payment_date (по возрастанию)
    - По сумме: ?ordering=amount (по возрастанию)
    - Обратная сортировка: ?ordering=-payment_date (по убыванию)
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters. OrderingFilter,
        filters.SearchFilter,
    ]

    filterset_class = PaymentFilter
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
    search_fields = ['user__email', 'paid_course__title', 'paid_lesson__title']

    @swagger_auto_schema(
        operation_summary="Получить список платежей",
        operation_description="""
        Возвращает список платежей с фильтрацией и сортировкой.

        ### Права доступа:
        - Администраторы: видят все платежи
        - Обычные пользователи: видят только свои платежи

        ### Параметры фильтрации:
        - paid_course: ID курса
        - paid_lesson: ID урока
        - payment_method: способ оплаты (cash/card)
        - payment_date_after: дата начала периода
        - payment_date_before: дата окончания периода

        ### Параметры сортировки:
        - ordering: поле для сортировки (payment_date, amount, -payment_date, -amount)
        """,
        manual_parameters=[
            openapi.Parameter(
                'paid_course',
                openapi.IN_QUERY,
                description="Фильтр по ID курса",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'paid_lesson',
                openapi.IN_QUERY,
                description="Фильтр по ID урока",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'payment_method',
                openapi.IN_QUERY,
                description="Способ оплаты",
                type=openapi.TYPE_STRING,
                enum=['cash', 'card']
            ),
            openapi.Parameter(
                'payment_date_after',
                openapi.IN_QUERY,
                description="Дата оплаты после (формат: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format='date'
            ),
            openapi.Parameter(
                'payment_date_before',
                openapi.IN_QUERY,
                description="Дата оплаты до (формат: YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format='date'
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Поле для сортировки",
                type=openapi.TYPE_STRING,
                enum=['payment_date', '-payment_date', 'amount', '-amount']
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Поиск по email пользователя, названию курса или урока",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: PaymentSerializer(many=True),
            401: "Пользователь не аутентифицирован"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создать новый платеж",
        operation_description="""
        Создает запись о платеже.

        ### Автоматические поля:
        - user: устанавливается как текущий пользователь
        - payment_date: устанавливается текущая дата (если не указана)

        ### Пример запроса:
               {
            "amount": 1000.00,
            "payment_method": "card",
            "paid_course": 1,
            "paid_lesson": null
        }
                """,
        request_body=PaymentSerializer,
        responses={
            201: PaymentSerializer,
            400: "Неверные данные",
            401: "Пользователь не аутентифицирован"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить детальную информацию о платеже",
        operation_description="""
        Возвращает детальную информацию о платеже по ID.

        ### Права доступа:
        - Владелец платежа (пользователь, совершивший платеж)
        - Администратор


        Обычные пользователи не могут просматривать чужие платежи.
        """,
        responses={
            200: PaymentSerializer,
            401: "Пользователь не аутентифицирован",
            403: "Нет прав для просмотра этого платежа",
            404: "Платеж не найден"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        """
        Ограничиваем доступ: пользователь видит только свои платежи.
        Администраторы видят все платежи.
        """
        # Для генерации схемы Swagger возвращаем пустой queryset
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()

        user = self.request.user

        if user.is_staff or user.is_superuser:
            return Payment.objects.all()
        else:
            return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        """При создании платежа автоматически устанавливаем текущего пользователя"""
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.

    ### Права доступа по действиям:
    - Создание: авторизованные пользователи, НЕ модераторы
    - Просмотр списка: только администраторы
    - Просмотр деталей: владелец профиля или модератор
    - Обновление: владелец профиля (не модератор) или модератор
    - Удаление: только владелец профиля, НЕ модератор
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsNotModerator]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsNotModerator, IsOwner]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        else:  # list
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        # Для Swagger
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()

        # Ограничиваем список пользователей - только администраторы
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()

        if user.is_staff or user.is_superuser:
            return User.objects.all()
        else:
            # Пользователи видят только свой профиль через retrieve
            return User.objects.filter(id=user.id)

    @swagger_auto_schema(
        operation_summary="Получить список пользователей",
        operation_description="""
        Возвращает список всех пользователей.

        ### Важно:
        - Только администраторы имеют доступ к этому эндпоинту
        - Обычные пользователи и модераторы получат ошибку 403
        """,
        responses={
            200: UserSerializer(many=True),
            401: "Пользователь не аутентифицирован",
            403: "Только администраторы могут просматривать список пользователей"
        }
    )
    def list(self, request, *args, **kwargs):
        """Ограничиваем список пользователей - только администраторы"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {"detail": "У вас нет прав для просмотра списка пользователей."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создать нового пользователя",
        operation_description="""
        Создает нового пользователя. Требуется авторизация.

        ### Ограничения:
        - Модераторы не могут создавать пользователей
        - Администраторы могут создавать пользователей
        - Обычные пользователи могут создавать пользователей

        ### Пример запроса:
               {
            "email": "newuser@example.com",
            "password": "password123",
            "phone": "+79991234567",
            "city": "Москва"
        }
                """,
        request_body=UserSerializer,
        responses={
            201: UserSerializer,
            400: "Неверные данные",
            401: "Пользователь не аутентифицирован",
            403: "Модераторы не могут создавать пользователей"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Регистрация пользователя (публичный эндпоинт)",
        operation_description="""
        Публичный эндпоинт для регистрации новых пользователей.
        Не требует авторизации.

        После успешной регистрации возвращает JWT токены для автоматической авторизации.

        ### Отличие от /create:
        - Не требует авторизации
        - Возвращает JWT токены
        - Использует UserRegistrationSerializer (с подтверждением пароля)
        """,
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="Пользователь зарегистрирован",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Неверные данные"
        }
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registration(self, request):
        """Эндпоинт для регистрации пользователя"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Получить/обновить свой профиль",
        operation_description="""
        Эндпоинт для работы с собственным профилем.

        ### Методы:
        - GET: получить свой профиль
        - PUT: полностью обновить свой профиль
        - PATCH: частично обновить свой профиль

        ### Особенности:
        - Используйте /api/users/me/ вместо /api/users/{id}/
        - Автоматически работает с профилем текущего пользователя
        """,
        methods=['get', 'put', 'patch']
    )
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Эндпоинт для работы с собственным профилем"""
        self.kwargs['pk'] = 'me'
        if request.method == 'GET':
            return self.retrieve(request)
        elif request.method == 'PUT':
            return self.update(request)
        elif request.method == 'PATCH':
            return self.partial_update(request)

    @swagger_auto_schema(
        operation_summary="Получить платежи пользователя",
        operation_description="""
        Возвращает все платежи указанного пользователя.

        ### Права доступа:
        - Администраторы: могут просматривать платежи любого пользователя
        - Владелец профиля: может просматривать свои платежи
        - Обычные пользователи: не могут просматривать чужие платежи
        """,
        responses={
            200: PaymentSerializer(many=True),
            401: "Пользователь не аутентифицирован",
            403: "Вы можете просматривать только свои платежи",
            404: "Пользователь не найден"
        }
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def payments(self, request, pk=None):
        """Получение платежей пользователя"""
        user = self.get_object()

        if not (request.user.is_staff or request.user.is_superuser or request.user == user):
            return Response(
                {"detail": "Вы можете просматривать только свои платежи."},
                status=status.HTTP_403_FORBIDDEN
            )

        payments = user.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def get_object(self):
        """Возвращает текущего пользователя или объект по ID"""
        if self.kwargs.get('pk') == 'me':
            return self.request.user
