from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""

    # Вложенный сериализатор для отображения уроков курса
    lessons = LessonSerializer(many=True, read_only=True)

    # Поле для подсчета уроков через SerializerMethodField (ЗАДАНИЕ 1)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'lessons', 'lesson_count')

    @staticmethod
    def get_lesson_count(obj):
        """Метод для получения количества уроков в курсе"""
        return obj.lessons.count()