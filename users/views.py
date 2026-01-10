from rest_framework import viewsets, filters
from django_filters import rest_framework as django_filters
from rest_framework.permissions import AllowAny
from .models import Payment
from .serializers import PaymentSerializer
from .filters import PaymentFilter


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для платежей с фильтрацией и сортировкой.

    Фильтрация:
    - ?ordering=payment_date (по возрастанию)
    - ?ordering=-payment_date (по убыванию)
    - ?paid_course=1 (фильтр по курсу)
    - ?paid_lesson=1 (фильтр по уроку)
    - ?payment_method=cash (фильтр по способу оплаты)
    - ?payment_method=transfer

    Примеры:
    - /api/users/payments/?ordering=-payment_date
    - /api/users/payments/?paid_course=1
    - /api/users/payments/?payment_method=cash&ordering=payment_date
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]

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
