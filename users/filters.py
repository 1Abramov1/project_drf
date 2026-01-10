import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    """Кастомный фильтр для платежей"""

    # Фильтр по дате (от и до)
    payment_date_from = django_filters.DateFilter(
        field_name='payment_date',
        lookup_expr='gte',
        label='Дата оплаты с'
    )

    payment_date_to = django_filters.DateFilter(
        field_name='payment_date',
        lookup_expr='lte',
        label='Дата оплаты по'
    )

    # Фильтр по сумме (от и до)
    amount_min = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        label='Сумма от'
    )

    amount_max = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        label='Сумма до'
    )

    class Meta:
        model = Payment
        fields = [
            'user',
            'paid_course',
            'paid_lesson',
            'payment_method',
            'payment_date_from',
            'payment_date_to',
            'amount_min',
            'amount_max',
        ]