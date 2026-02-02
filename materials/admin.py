from django.contrib import admin
from .models import Course, Lesson, Subscription


class LessonInline(admin.TabularInline):
    """Встроенное отображение уроков в курсе"""
    model = Lesson
    extra = 1
    fields = ('title', 'description', 'video_link', 'owner')
    readonly_fields = ('created_at', 'updated_at')


class SubscriptionInline(admin.TabularInline):
    """Встроенное отображение подписок в курсе"""
    model = Subscription
    extra = 0
    fields = ('user', 'is_active', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = True
    show_change_link = True
    max_num = 10  # Ограничиваем количество отображаемых подписок


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Админ-панель для курсов"""

    list_display = ('title', 'owner', 'price', 'stripe_price_id', 'subscriptions_count', 'lesson_count', 'created_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('title', 'description')
    list_editable = ('price',)  # Можно редактировать цену прямо в списке
    inlines = [LessonInline, SubscriptionInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'preview', 'description', 'price', 'owner')
        }),
        ('Stripe интеграция', {
            'fields': ('stripe_product_id', 'stripe_price_id'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def subscriptions_count(self, obj):
        """Количество активных подписок на курс"""
        return obj.subscriptions.filter(is_active=True).count()

    subscriptions_count.short_description = 'Подписчиков'

    def lesson_count(self, obj):
        """Количество уроков в курсе"""
        return obj.lessons.count()

    lesson_count.short_description = 'Уроков'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Админ-панель для уроков"""

    list_display = ('title', 'course', 'owner', 'created_at')
    list_filter = ('course', 'owner', 'created_at')
    search_fields = ('title', 'description', 'video_link')

    fieldsets = (
        (None, {
            'fields': ('title', 'course', 'description')
        }),
        ('Медиа', {
            'fields': ('preview', 'video_link')
        }),
        ('Владелец', {
            'fields': ('owner',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ-панель для подписок"""

    list_display = ('id', 'user_email', 'course_title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'course')
    search_fields = ('user__email', 'course__title')
    list_editable = ('is_active',)
    list_per_page = 20
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'course', 'is_active')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at',)

    def user_email(self, obj):
        """Email пользователя"""
        return obj.user.email

    user_email.short_description = 'Пользователь'
    user_email.admin_order_field = 'user__email'

    def course_title(self, obj):
        """Название курса"""
        return obj.course.title

    course_title.short_description = 'Курс'
    course_title.admin_order_field = 'course__title'

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related('user', 'course')
