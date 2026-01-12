from rest_framework import filters, viewsets, permissions, status
from django_filters import rest_framework as django_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Payment, User
from .filters import PaymentFilter
from .serializers import UserSerializer, UserRegistrationSerializer, PaymentSerializer

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


class UserRegistrationView(APIView):
    """Отдельный View для регистрации, полностью публичный"""
    permission_classes = [AllowAny]
    authentication_classes = []

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
    ViewSet для платежей с фильтрацией и сортировкой.
    Все операции требуют JWT-авторизации.
    Пользователь видит только свои платежи.
    """

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Изменено с AllowAny на IsAuthenticated

    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]

    # Используем кастомный фильтр
    filterset_class = PaymentFilter

    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
    search_fields = ['user__email', 'paid_course__title', 'paid_lesson__title']

    def get_queryset(self):
        """
        Ограничиваем доступ: пользователь видит только свои платежи.
        Администраторы видят все платежи.
        """
        user = self.request.user

        if user.is_staff or user.is_superuser:
            # Администраторы видят все платежи
            return Payment.objects.all()
        else:
            # Обычные пользователи видят только свои платежи
            return Payment.objects.filter(user=user)

    def perform_create(self, serializer):
        """При создании платежа автоматически устанавливаем текущего пользователя"""
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций с пользователями"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Настройка прав доступа для разных действий"""
        if self.action in ['create', 'registration', 'token', 'refresh', 'verify']:
            # Эти действия доступны всем (регистрация и получение токена)
            permission_classes = [permissions.AllowAny]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'me', 'payments']:
            # Работа с профилем и платежами требует авторизации
            # Проверяем, что пользователь работает со своим профилем
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Список пользователей только для админов
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


    def get_object(self):
        """Возвращает текущего пользователя или объект по ID"""
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()

    def list(self, request, *args, **kwargs):
        """Ограничиваем список пользователей - только администраторы"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {"detail": "У вас нет прав для просмотра списка пользователей."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def registration(self, request):
        """Эндпоинт для регистрации пользователя"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Автоматическая авторизация после регистрации
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Эндпоинт для работы с собственным профилем"""
        self.kwargs['pk'] = 'me'
        if request.method == 'GET':
            return self.retrieve(request)
        elif request.method == 'PUT':
            return self.update(request)
        elif request.method == 'PATCH':
            return self.partial_update(request)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def payments(self, request, pk=None):
        """Получение платежей пользователя"""
        user = self.get_object()

        # Проверяем права доступа
        if not (request.user.is_staff or request.user.is_superuser or request.user == user):
            return Response(
                {"detail": "Вы можете просматривать только свои платежи."},
                status=status.HTTP_403_FORBIDDEN
            )

        payments = user.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
