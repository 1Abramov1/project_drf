from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели User с email вместо username"""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и возвращает пользователя с email и паролем"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и возвращает суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email"""

    # Убираем поле username
    username = None

    # Основные поля
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )

    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Phone number in format: +79991234567')
    )

    city = models.CharField(
        _('city'),
        max_length=100,
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        _('avatar'),
        upload_to='users/avatars/',
        blank=True,
        null=True,
        help_text=_('Upload your profile picture')
    )

    # Устанавливаем email как поле для аутентификации
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email уже обязателен

    # Указываем кастомный менеджер
    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Возвращает полное имя пользователя"""
        return f"{self.first_name} {self.last_name}".strip()


class Payment(models.Model):
    """Модель платежей"""

    class PaymentMethod(models.TextChoices):
        """Способы оплаты"""
        CASH = 'cash', _('Наличные')
        TRANSFER = 'transfer', _('Перевод на счет')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('пользователь'),
        help_text=_('Пользователь, совершивший платеж')
    )

    payment_date = models.DateTimeField(
        _('дата оплаты'),
        auto_now_add=True,
        help_text=_('Дата и время совершения платежа')
    )

    # Ссылка на курс (опционально)
    paid_course = models.ForeignKey(
        'materials.Course',  # ссылка на модель Course из приложения materials
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('оплаченный курс'),
        help_text=_('Курс, за который произведена оплата')
    )

    # Ссылка на урок (опционально)
    paid_lesson = models.ForeignKey(
        'materials.Lesson',  # ссылка на модель Lesson из приложения materials
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_('оплаченный урок'),
        help_text=_('Урок, за который произведена оплата')
    )

    amount = models.DecimalField(
        _('сумма оплаты'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Сумма оплаты в рублях')
    )

    payment_method = models.CharField(
        _('способ оплаты'),
        max_length=10,
        choices=PaymentMethod.choices,
        default=PaymentMethod.TRANSFER,
        help_text=_('Способ осуществления платежа')
    )

    class Meta:
        verbose_name = _('платеж')
        verbose_name_plural = _('платежи')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_date']),
            models.Index(fields=['user', 'payment_date']),
        ]

    def __str__(self):
        if self.paid_course:
            return f"{self.user.email} - {self.paid_course.title} - {self.amount} руб."
        elif self.paid_lesson:
            return f"{self.user.email} - {self.paid_lesson.title} - {self.amount} руб."
        return f"{self.user.email} - {self.amount} руб."

    def clean(self):
        """Валидация: либо курс, либо урок, но не оба одновременно"""
        from django.core.exceptions import ValidationError

        if self.paid_course and self.paid_lesson:
            raise ValidationError(_('Платеж может быть только за курс ИЛИ за урок, но не за оба одновременно.'))

        if not self.paid_course and not self.paid_lesson:
            raise ValidationError(_('Укажите либо курс, либо урок за который произведена оплата.'))
