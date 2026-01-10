from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Payment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ-панель для кастомного пользователя"""

    # Поля для отображения в списке
    list_display = ('email', 'first_name', 'last_name', 'city', 'phone', 'is_staff')
    list_filter = ('is_staff', 'is_active', 'city')
    search_fields = ('email', 'first_name', 'last_name', 'phone')

    # Порядок полей в форме
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Поля при создании пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )

    ordering = ('email',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Админ-панель для платежей"""

    list_display = ('user', 'payment_date', 'paid_course', 'paid_lesson', 'amount', 'payment_method')
    list_filter = ('payment_date', 'payment_method', 'user')
    search_fields = ('user__email', 'paid_course__title', 'paid_lesson__title')
    date_hierarchy = 'payment_date'
    readonly_fields = ('payment_date',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'payment_date')
        }),
        ('Оплата', {'fields': ('paid_course', 'paid_lesson', 'amount', 'payment_method')
        }),
    )
