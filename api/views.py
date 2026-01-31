from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from api.serializers import StripeCheckoutSerializer
from api.services import stripe_service
from materials.models import Course


@api_view(['GET'])
def api_root(request):
    """Корневой endpoint API"""
    return Response({
        'message': 'Welcome to Education Platform API',
        'endpoints': {
            'materials/courses/': 'Course CRUD',
            'materials/lessons/': 'Lesson CRUD',
            'users/users/': 'User management',
            'api/payments/create-checkout/': 'Create Stripe checkout',
        }
    })


class PaymentViewSet(viewsets.ViewSet):
    """ViewSet для работы с оплатой через Stripe"""
    permission_classes = [IsAuthenticated]

    # Явно указываем basename для Swagger
    swagger_tags = ['Stripe API']

    @action(detail=False, methods=['post'], url_path='create-checkout')
    def create_checkout(self, request):
        """
        Создает Stripe Checkout сессию для оплаты курса.
        Пример запроса:
        POST /api/payments/create-checkout/
        {
            "course_id": 1,
            "success_url": "http://localhost:8000/success",
            "cancel_url": "http://localhost:8000/cancel"
        }
        """
        serializer = StripeCheckoutSerializer(data=request.data)
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            success_url = serializer.validated_data['success_url']
            cancel_url = serializer.validated_data['cancel_url']

            # Получаем курс
            course = get_object_or_404(Course, id=course_id)

            # Проверяем, что у курса есть цена в Stripe
            if not course.stripe_price_id:
                return Response(
                    {
                        "error": "Для этого курса не настроена оплата",
                        "detail": "Установите цену > 0 для курса"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Создаем сессию оплаты
            try:
                session = stripe_service.create_checkout_session(
                    price_id=course.stripe_price_id,
                    success_url=success_url,
                    cancel_url=cancel_url,
                    client_reference_id=str(course.id),
                    metadata={
                        'course_id': str(course.id),
                        'course_title': course.title,
                        'user_id': str(request.user.id),
                    }
                )

                return Response({
                    "checkout_url": session['url'],
                    "session_id": session['id'],
                    "course": {
                        "id": course.id,
                        "title": course.title,
                        "price": str(course.price)
                    }
                })

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)