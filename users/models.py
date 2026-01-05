from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


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
