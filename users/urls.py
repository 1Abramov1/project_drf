from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from . import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet, basename='payment')
# UserViewSet регистрируем ПОСЛЕ явных путей
router.register(r'', views.UserViewSet, basename='user')

# ЯВНЫЕ пути ДО router.urls
urlpatterns = [
    # Отдельный view для регистрации (публичный)
    path('register/', views.UserRegistrationView.as_view(), name='register'),

    # JWT эндпоинты
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Router.urls В САМОМ КОНЦЕ
    path('', include(router.urls)),
]

