from django.contrib import admin
from .models import Course, Lesson


class LessonInline(admin.TabularInline):
    """Встроенное отображение уроков в курсе"""
    model = Lesson
    extra = 1
    fields = ('title', 'description', 'video_link', 'owner')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Админ-панель для курсов"""

    list_display = ('title', 'owner', 'lesson_count', 'created_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('title', 'description')
    inlines = [LessonInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'preview', 'description', 'owner')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


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
        ('Media', {'fields': ('preview', 'video_link')
        }),
        ('Owner', {
            'fields': ('owner',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
