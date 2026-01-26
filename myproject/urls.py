from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 1. конфигурация схемы
schema_view = get_schema_view(
    openapi.Info(
        title="DRF Education Platform API",
        default_version='v1',
        description="""API для управления курсами, уроками и платежами

        ### Основные разделы:
        - **Materials** - Курсы и уроки
        - **Users** - Пользователи и платежи  
        - **Stripe API** - Оплата курсов через Stripe

        ### Авторизация:
        Используйте JWT токены через `/api/users/token/`
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API URLs
    path('api/', include('api.urls')), # API
    path('api/materials/', include('materials.urls')),  # Материалы
    path('api/users/', include('users.urls')),          # Пользователи

    # Документация
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
