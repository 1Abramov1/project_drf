from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором"""

    def has_permission(self, request, view):
        # Проверяем, аутентифицирован ли пользователь
        if not request.user.is_authenticated:
            return False

        # Проверяем, принадлежит ли пользователь к группе 'moderators'
        return request.user.groups.filter(name='moderators').exists()


class IsOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Суперпользователи и администраторы имеют все права
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Модераторы могут всё
        if request.user.groups.filter(name='moderators').exists():
            return True

        # Проверяем, является ли пользователь владельцем
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        # Проверяем, является ли пользователь владельцем объекта
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsNotModerator(permissions.BasePermission):
    """Проверяет, что пользователь НЕ является модератором"""

    def has_permission(self, request, view):
        # Если пользователь не аутентифицирован - сразу нет
        if not request.user.is_authenticated:
            return False

        # Проверяем, что пользователь НЕ в группе модераторов
        return not request.user.groups.filter(name='moderators').exists()
