from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций с курсами.
    Использует ViewSet как указано в задании.
    ВСЕ операции требуют JWT-авторизации.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]  # Изменено с AllowAny на IsAuthenticated

    def perform_create(self, serializer):
        """При создании курса автоматически устанавливаем текущего пользователя как владельца"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Получить все уроки курса"""
        # Получаем курс по pk
        course = get_object_or_404(Course, pk=pk)
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonListCreateView(generics.ListCreateAPIView):
    """
    Generic View для получения списка уроков и создания нового.
    Использует Generic-классы как указано в задании.
    ВСЕ операции требуют JWT-авторизации.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]  # Изменено с AllowAny на IsAuthenticated

    def perform_create(self, serializer):
        """При создании урока автоматически устанавливаем текущего пользователя как владельца"""
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Generic View для получения, обновления и удаления урока.
    Использует Generic-классы как указано в задании.
    ВСЕ операции требуют JWT-авторизации.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]  # Изменено с AllowAny на IsAuthenticated