from rest_framework import serializers
from .models import Payment
from materials.serializers import CourseSerializer, LessonSerializer


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""

    # Вложенные сериализаторы для детальной информации
    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_detail = CourseSerializer(source='paid_course', read_only=True)
    lesson_detail = LessonSerializer(source='paid_lesson', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date',
            'paid_course', 'course_detail', 'paid_lesson', 'lesson_detail',
            'amount', 'payment_method'
        ]
        read_only_fields = ('payment_date',)