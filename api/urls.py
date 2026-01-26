from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import api_root, PaymentViewSet

router = DefaultRouter()
router.register(r'stripe-payments', PaymentViewSet, basename='stripe-payment')  # ⭐️ Изменили имя

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
]
