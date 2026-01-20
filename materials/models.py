from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError


class Course(models.Model):
    """Модель курса"""

    title = models.CharField(
        _('title'),
        max_length=200,
        help_text=_('Course title')
    )

    preview = models.ImageField(
        _('preview image'),
        upload_to='courses/previews/',
        blank=True,
        null=True,
        help_text=_('Course preview image')
    )

    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
        help_text=_('Detailed course description')
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name=_('owner')
    )

    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')
        ordering = ['-created_at']

    def __str__(self):  # ← ДВА подчеркивания с каждой стороны
        return self.title

    @property
    def lesson_count(self):
        """Количество уроков в курсе"""
        return self.lessons.count()


class Lesson(models.Model):
    """Модель урока"""

    title = models.CharField(
        _('title'),
        max_length=200,
        help_text=_('Lesson title')
    )

    description = models.TextField(
        _('description'),
        blank=True,
        null=True,
        help_text=_('Detailed lesson description')
    )

    preview = models.ImageField(
        _('preview image'),
        upload_to='lessons/previews/',
        blank=True,
        null=True,
        help_text=_('Lesson preview image')
    )

    video_link = models.URLField(
        _('video link'),
        max_length=500,
        blank=True,
        null=True,
        help_text=_('Link to video lesson (YouTube only)')
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('course'),
        help_text=_('Course this lesson belongs to')
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name=_('owner')
    )

    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        ordering = ['created_at']

    def __str__(self):  # ← ДВА подчеркивания с каждой стороны
        return f"{self.title} ({self.course.title})"

    def clean(self):
        """Валидация на уровне модели для проверки YouTube ссылок"""
        from .validators import validate_youtube_url

        # Проверяем ссылку на видео, если она указана
        if self.video_link:
            validate_youtube_url(self.video_link)

        super().clean()

    def save(self, *args, **kwargs):
        """Вызываем clean() перед сохранением"""
        self.clean()
        super().save(*args, **kwargs)


class Subscription(models.Model):
    """
    Модель подписки пользователя на курс.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('user')
    )

    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=_('course')
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        unique_together = ['user', 'course']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} → {self.course.title}"