from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создаем router для ViewSet курсов
router = DefaultRouter()
router.register(r'courses', views.CourseViewSet, basename='course')

urlpatterns = [
    # Маршруты для курсов (через ViewSet)
    path('', include(router.urls)),

    # Маршруты для уроков (через Generic Views)
    path('lessons/', views.LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', views.LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
]