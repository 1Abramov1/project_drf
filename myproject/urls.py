from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # если есть API приложение
    path('api/materials/', include('materials.urls')),  # подключаем материалы
    path('api/users/', include('users.urls')),
]
