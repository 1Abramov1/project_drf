from rest_framework import serializers
from materials.models import Course


class StripeCheckoutSerializer(serializers.Serializer):
    """Сериализатор для создания сессии оплаты Stripe"""
    course_id = serializers.IntegerField(required=True)
    success_url = serializers.URLField(required=True)
    cancel_url = serializers.URLField(required=True)

    def validate_course_id(self, value):
        if not Course.objects.filter(id=value).exists():
            raise serializers.ValidationError("Курс не найден")
        return value