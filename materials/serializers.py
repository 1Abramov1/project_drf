from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url  # ← импортируем функцию


class LessonSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        print(f"DEBUG LessonSerializer: instance={kwargs.get('instance')}")  # Что сериализуем?
        super().__init__(*args, **kwargs)
    # Добавляем валидатор прямо к полю
    video_link = serializers.URLField(
        validators=[validate_youtube_url],  # ← используем функцию
        required=False,
        allow_blank=True
    )

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')



# Остальные сериализаторы без изменений
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'course', 'created_at']
        read_only_fields = ['user', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.IntegerField(source='lessons.count', read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'preview', 'description',
            'created_at', 'updated_at', 'owner',
            'lessons', 'lesson_count', 'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        """
        Определяет, подписан ли текущий пользователь на этот курс.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Проверяем, есть ли подписка у этого пользователя на этот курс
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False
